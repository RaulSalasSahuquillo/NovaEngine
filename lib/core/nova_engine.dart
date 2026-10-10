import '../models/order_receipt.dart';
import '../models/portfolio_item.dart';
import '../models/transaction.dart';
import '../services/analytics_service.dart';
import '../services/coingecko_service.dart';
import '../services/currency_service.dart';
import '../services/storage_service.dart';
import '../services/tax_service.dart';
import '../services/yahoo_finance_service.dart';

/// Headless quantitative execution runtime and portfolio accounting engine.
class NovaEngine {
  final String userCountry;
  final double initialCapital;
  final YahooFinanceService yahooService;
  final CoinGeckoService coinGeckoService;
  final StorageProvider? storageProvider;

  double cashBalance;
  final List<PortfolioItem> holdings = [];
  final List<Transaction> transactions = [];

  NovaEngine({
    this.userCountry = 'ES',
    this.cashBalance = 100000.0,
    YahooFinanceService? yahoo,
    CoinGeckoService? coinGecko,
    this.storageProvider,
  })  : initialCapital = cashBalance,
        yahooService = yahoo ?? YahooFinanceService(),
        coinGeckoService = coinGecko ?? CoinGeckoService();

  double get totalInvested =>
      holdings.fold(0.0, (sum, item) => sum + item.totalValue);

  double get totalNetWorth => cashBalance + totalInvested;

  double get totalProfitLoss => totalNetWorth - initialCapital;

  double get totalProfitLossPercent =>
      initialCapital > 0 ? (totalProfitLoss / initialCapital) * 100.0 : 0.0;

  PortfolioItem? getPosition(String assetId) {
    final clean = assetId.toUpperCase().trim();
    final index = holdings.indexWhere((h) => h.assetId.toUpperCase() == clean);
    return index >= 0 ? holdings[index] : null;
  }

  Future<void> _persistState() async {
    if (storageProvider != null) {
      await storageProvider!.saveState(
        cashBalance: cashBalance,
        initialCapital: initialCapital,
        holdings: holdings,
        transactions: transactions,
      );
    }
  }

  /// Restores state from configured storage provider if available.
  Future<bool> loadFromStorage() async {
    if (storageProvider == null) return false;
    final state = await storageProvider!.loadState();
    if (state == null) return false;

    cashBalance = (state['cash_balance'] as num?)?.toDouble() ?? cashBalance;
    holdings.clear();
    final rawPositions = state['positions'] as List<dynamic>?;
    if (rawPositions != null) {
      for (final p in rawPositions) {
        holdings.add(PortfolioItem.fromJson(p as Map<String, dynamic>));
      }
    }

    transactions.clear();
    final rawTx = state['transactions'] as List<dynamic>?;
    if (rawTx != null) {
      for (final t in rawTx) {
        transactions.add(Transaction.fromJson(t as Map<String, dynamic>));
      }
    }
    return true;
  }

  /// Executes a buy order with statutory friction evaluation and currency harmonization.
  Future<OrderReceipt> buy({
    required String assetId,
    required double quantity,
    double? pricePerUnit,
    String? assetName,
    AssetClass assetType = AssetClass.stock,
    String? countryCode,
  }) async {
    if (quantity <= 0) {
      return OrderReceipt(
        assetId: assetId,
        assetName: assetName ?? assetId,
        assetType: assetType,
        side: OrderSide.buy,
        quantity: quantity,
        pricePerUnit: 0.0,
        totalGrossAmount: 0.0,
        netAmount: 0.0,
        countryCode: countryCode ?? userCountry,
        status: ExecutionStatus.rejected,
        rejectionReason: 'Order quantity must be positive.',
      );
    }

    final activeCountry = (countryCode ?? userCountry).toUpperCase().trim();
    final taxProfile = TaxService.getProfile(activeCountry);
    final cleanId = assetId.trim();

    double resolvedPrice = pricePerUnit ?? 0.0;
    String resolvedName = assetName ?? cleanId;
    String quoteCurrency = taxProfile.currencyCode;

    if (pricePerUnit == null) {
      if (assetType == AssetClass.stock) {
        final quote = await yahooService.getQuote(cleanId);
        if (quote == null) {
          return OrderReceipt(
            assetId: cleanId,
            assetName: resolvedName,
            assetType: assetType,
            side: OrderSide.buy,
            quantity: quantity,
            pricePerUnit: 0.0,
            totalGrossAmount: 0.0,
            netAmount: 0.0,
            countryCode: activeCountry,
            status: ExecutionStatus.rejected,
            rejectionReason: 'Unable to retrieve live quote for stock $cleanId.',
          );
        }
        resolvedPrice = quote.currentPrice;
        resolvedName = quote.name;
        quoteCurrency = quote.currency;
      } else {
        final cQuote = await coinGeckoService.getCrypto(cleanId);
        if (cQuote == null) {
          return OrderReceipt(
            assetId: cleanId,
            assetName: resolvedName,
            assetType: assetType,
            side: OrderSide.buy,
            quantity: quantity,
            pricePerUnit: 0.0,
            totalGrossAmount: 0.0,
            netAmount: 0.0,
            countryCode: activeCountry,
            status: ExecutionStatus.rejected,
            rejectionReason: 'Unable to retrieve live quote for crypto $cleanId.',
          );
        }
        resolvedPrice = cQuote.currentPrice;
        resolvedName = cQuote.name;
        quoteCurrency = 'EUR';
      }
    }

    // Convert quote price to the jurisdiction execution currency
    final priceInUserCurr = CurrencyService.convert(
      amount: resolvedPrice,
      fromCurrency: quoteCurrency,
      toCurrency: taxProfile.currencyCode,
    );

    final breakdown = TaxService.calculateBuyBreakdown(
      quantity: quantity,
      pricePerUnit: priceInUserCurr,
      isStock: assetType == AssetClass.stock,
      countryCode: activeCountry,
    );

    // Convert costs to canonical base EUR for ledger accounting
    final totalCostInEur = CurrencyService.toEur(breakdown.netAmount, taxProfile.currencyCode);
    final unitPriceInEur = CurrencyService.toEur(priceInUserCurr, taxProfile.currencyCode);

    // Assert solvency before debiting ledger
    if (totalCostInEur > cashBalance + 1e-4) {
      return OrderReceipt(
        assetId: cleanId,
        assetName: resolvedName,
        assetType: assetType,
        side: OrderSide.buy,
        quantity: quantity,
        pricePerUnit: priceInUserCurr,
        totalGrossAmount: breakdown.grossAmount,
        netAmount: breakdown.netAmount,
        countryCode: activeCountry,
        status: ExecutionStatus.rejected,
        rejectionReason: 'Insufficient funds. Required: €${totalCostInEur.toStringAsFixed(2)}, Available: €${cashBalance.toStringAsFixed(2)}',
      );
    }

    // Update position with weighted average acquisition cost
    final existingPosition = getPosition(cleanId);
    if (existingPosition != null) {
      existingPosition.addVolume(quantity, unitPriceInEur);
    } else {
      holdings.add(
        PortfolioItem(
          assetId: cleanId,
          assetName: resolvedName,
          assetType: assetType.name,
          quantity: quantity,
          avgBuyPrice: unitPriceInEur,
          currentPrice: unitPriceInEur,
        ),
      );
    }

    // Debit cash balance
    cashBalance -= totalCostInEur;

    final receipt = OrderReceipt(
      assetId: cleanId,
      assetName: resolvedName,
      assetType: assetType,
      side: OrderSide.buy,
      quantity: quantity,
      pricePerUnit: priceInUserCurr,
      totalGrossAmount: breakdown.grossAmount,
      brokerFee: breakdown.brokerFee,
      transactionTax: breakdown.transactionTax + breakdown.exchangeFee,
      capitalGainsTax: 0.0,
      netAmount: breakdown.netAmount,
      countryCode: activeCountry,
      status: ExecutionStatus.filled,
    );

    transactions.insert(
      0,
      Transaction(
        id: receipt.id,
        assetId: cleanId,
        assetName: resolvedName,
        assetType: assetType.name,
        type: 'buy',
        quantity: quantity,
        pricePerUnit: priceInUserCurr,
        totalAmount: breakdown.grossAmount,
        brokerFee: breakdown.brokerFee,
        transactionTax: breakdown.transactionTax + breakdown.exchangeFee,
        capitalGainsTax: 0.0,
        netAmount: breakdown.netAmount,
        countryCode: activeCountry,
        timestamp: receipt.timestamp,
      ),
    );

    await _persistState();
    return receipt;
  }

  /// Executes a sell order, withholds capital gains tax, and credits net proceeds.
  Future<OrderReceipt> sell({
    required String assetId,
    required double quantity,
    double? pricePerUnit,
    AssetClass assetType = AssetClass.stock,
    String? countryCode,
  }) async {
    if (quantity <= 0) {
      return OrderReceipt(
        assetId: assetId,
        assetName: assetId,
        assetType: assetType,
        side: OrderSide.sell,
        quantity: quantity,
        pricePerUnit: 0.0,
        totalGrossAmount: 0.0,
        netAmount: 0.0,
        countryCode: countryCode ?? userCountry,
        status: ExecutionStatus.rejected,
        rejectionReason: 'Sale quantity must be positive.',
      );
    }

    final cleanId = assetId.trim();
    final position = getPosition(cleanId);

    if (position == null || position.quantity < quantity - 1e-6) {
      final held = position?.quantity ?? 0.0;
      return OrderReceipt(
        assetId: cleanId,
        assetName: position?.assetName ?? cleanId,
        assetType: assetType,
        side: OrderSide.sell,
        quantity: quantity,
        pricePerUnit: 0.0,
        totalGrossAmount: 0.0,
        netAmount: 0.0,
        countryCode: countryCode ?? userCountry,
        status: ExecutionStatus.rejected,
        rejectionReason: 'Insufficient position. Held: $held, Requested: $quantity',
      );
    }

    final activeCountry = (countryCode ?? userCountry).toUpperCase().trim();
    final taxProfile = TaxService.getProfile(activeCountry);

    double resolvedPrice = pricePerUnit ?? 0.0;
    String quoteCurrency = taxProfile.currencyCode;

    if (pricePerUnit == null) {
      if (assetType == AssetClass.stock) {
        final quote = await yahooService.getQuote(cleanId);
        if (quote == null) {
          return OrderReceipt(
            assetId: cleanId,
            assetName: position.assetName,
            assetType: assetType,
            side: OrderSide.sell,
            quantity: quantity,
            pricePerUnit: 0.0,
            totalGrossAmount: 0.0,
            netAmount: 0.0,
            countryCode: activeCountry,
            status: ExecutionStatus.rejected,
            rejectionReason: 'Unable to retrieve live quote for stock $cleanId.',
          );
        }
        resolvedPrice = quote.currentPrice;
        quoteCurrency = quote.currency;
      } else {
        final cQuote = await coinGeckoService.getCrypto(cleanId);
        if (cQuote == null) {
          return OrderReceipt(
            assetId: cleanId,
            assetName: position.assetName,
            assetType: assetType,
            side: OrderSide.sell,
            quantity: quantity,
            pricePerUnit: 0.0,
            totalGrossAmount: 0.0,
            netAmount: 0.0,
            countryCode: activeCountry,
            status: ExecutionStatus.rejected,
            rejectionReason: 'Unable to retrieve live quote for crypto $cleanId.',
          );
        }
        resolvedPrice = cQuote.currentPrice;
        quoteCurrency = 'EUR';
      }
    }

    // Convert execution price and historical cost basis to jurisdiction currency
    final priceInUserCurr = CurrencyService.convert(
      amount: resolvedPrice,
      fromCurrency: quoteCurrency,
      toCurrency: taxProfile.currencyCode,
    );
    final avgCostInUserCurr = CurrencyService.fromEur(
      position.avgBuyPrice,
      taxProfile.currencyCode,
    );

    final breakdown = TaxService.calculateSellBreakdown(
      quantity: quantity,
      pricePerUnit: priceInUserCurr,
      avgBuyPrice: avgCostInUserCurr,
      isStock: assetType == AssetClass.stock,
      countryCode: activeCountry,
    );

    // Convert net proceeds to canonical EUR
    final netProceedsInEur = CurrencyService.toEur(breakdown.netAmount, taxProfile.currencyCode);
    final exitPriceInEur = CurrencyService.toEur(priceInUserCurr, taxProfile.currencyCode);

    // Liquidate or reduce position volume
    if (quantity >= position.quantity - 1e-6) {
      holdings.remove(position);
    } else {
      position.reduceVolume(quantity, exitPriceInEur);
    }

    // Credit net proceeds to cash balance
    cashBalance += netProceedsInEur;

    final receipt = OrderReceipt(
      assetId: cleanId,
      assetName: position.assetName,
      assetType: assetType,
      side: OrderSide.sell,
      quantity: quantity,
      pricePerUnit: priceInUserCurr,
      totalGrossAmount: breakdown.grossAmount,
      brokerFee: breakdown.brokerFee,
      transactionTax: breakdown.transactionTax + breakdown.exchangeFee,
      capitalGainsTax: breakdown.capitalGainsTax,
      netAmount: breakdown.netAmount,
      countryCode: activeCountry,
      status: ExecutionStatus.filled,
    );

    transactions.insert(
      0,
      Transaction(
        id: receipt.id,
        assetId: cleanId,
        assetName: position.assetName,
        assetType: assetType.name,
        type: 'sell',
        quantity: quantity,
        pricePerUnit: priceInUserCurr,
        totalAmount: breakdown.grossAmount,
        brokerFee: breakdown.brokerFee,
        transactionTax: breakdown.transactionTax + breakdown.exchangeFee,
        capitalGainsTax: breakdown.capitalGainsTax,
        netAmount: breakdown.netAmount,
        countryCode: activeCountry,
        timestamp: receipt.timestamp,
      ),
    );

    await _persistState();
    return receipt;
  }

  /// Synchronizes spot valuations across all active holdings in the portfolio.
  Future<void> syncLivePrices() async {
    final stockSymbols = holdings.where((h) => h.isStock).map((h) => h.assetId).toList();
    final cryptoIds = holdings.where((h) => h.isCrypto).map((h) => h.assetId).toList();

    if (stockSymbols.isNotEmpty) {
      for (final sym in stockSymbols) {
        final quote = await yahooService.getQuote(sym);
        if (quote != null) {
          final pos = getPosition(sym);
          if (pos != null) {
            pos.currentPrice = CurrencyService.toEur(quote.currentPrice, quote.currency);
          }
        }
      }
    }

    if (cryptoIds.isNotEmpty) {
      for (final cid in cryptoIds) {
        final cQuote = await coinGeckoService.getCrypto(cid);
        if (cQuote != null) {
          final pos = getPosition(cid);
          if (pos != null) {
            pos.currentPrice = cQuote.currentPrice;
          }
        }
      }
    }
  }

  /// Compiles a complete financial statement converted to the target currency.
  Map<String, dynamic> getStatement({String? currencyCode}) {
    final targetCurr = (currencyCode ?? TaxService.getProfile(userCountry).currencyCode).toUpperCase();
    final profile = TaxService.getProfile(userCountry);

    final cash = CurrencyService.fromEur(cashBalance, targetCurr);
    final invested = CurrencyService.fromEur(totalInvested, targetCurr);
    final netWorth = cash + invested;
    final pl = CurrencyService.fromEur(totalProfitLoss, targetCurr);

    final List<Map<String, dynamic>> holdingsData = holdings.map((pos) {
      return {
        'asset_id': pos.assetId,
        'name': pos.assetName,
        'type': pos.assetType.toUpperCase(),
        'quantity': pos.quantity,
        'avg_buy_price': CurrencyService.fromEur(pos.avgBuyPrice, targetCurr),
        'current_price': CurrencyService.fromEur(pos.currentPrice, targetCurr),
        'total_value': CurrencyService.fromEur(pos.totalValue, targetCurr),
        'profit_loss': CurrencyService.fromEur(pos.profitLoss, targetCurr),
        'profit_loss_pct': pos.profitLossPercent,
      };
    }).toList();

    return {
      'currency': targetCurr,
      'currency_symbol': profile.currencySymbol,
      'cash_balance': cash,
      'invested_value': invested,
      'total_net_worth': netWorth,
      'total_profit_loss': pl,
      'total_profit_loss_pct': totalProfitLossPercent,
      'holdings': holdingsData,
    };
  }

  /// Evaluates risk, drawdown, and efficiency metrics on the portfolio ledger.
  PerformanceMetrics evaluatePerformance() {
    return AnalyticsService.evaluate(
      netWorth: totalNetWorth,
      initialCapital: initialCapital,
      transactions: transactions,
    );
  }
}
