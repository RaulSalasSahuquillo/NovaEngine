import 'dart:io';
import 'package:args/command_runner.dart';
import 'package:novaengine/novaengine.dart';

void main(List<String> arguments) async {
  final runner = CommandRunner(
    'novaengine',
    'NovaEngine: Headless Quantitative Trading, Market Feeds and Fiscal Auditing Core.',
  )
    ..addCommand(QuoteCommand())
    ..addCommand(CryptoCommand())
    ..addCommand(BuyCommand())
    ..addCommand(SellCommand())
    ..addCommand(StatementCommand())
    ..addCommand(TaxesCommand());

  try {
    await runner.run(arguments);
  } on UsageException catch (e) {
    print(e.message);
    print(e.usage);
    exit(64);
  } catch (e) {
    print('Execution Error: $e');
    exit(1);
  }
}

class QuoteCommand extends Command {
  @override
  final name = 'quote';
  @override
  final description = 'Fetch a stock or ETF quote.';

  QuoteCommand() {
    argParser.addOption('country', abbr: 'c', defaultsTo: 'ES', help: 'Country tax code.');
  }

  @override
  void run() async {
    if (argResults?.rest.isEmpty ?? true) {
      print('Error: Specify a ticker symbol, e.g.: novaengine quote AAPL');
      exit(1);
    }
    final symbol = argResults!.rest.first;
    final yahoo = YahooFinanceService();
    final quote = await yahoo.getQuote(symbol);

    if (quote == null) {
      print("Error: Quote for '$symbol' not found.");
      exit(1);
    }

    print('========================================');
    print('  TICKER QUOTE: ${quote.symbol}');
    print('========================================');
    print('  Name:           ${quote.name}');
    print('  Price:          ${quote.currentPrice.toStringAsFixed(2)} ${quote.currency}');
    print('  Change:         ${quote.change >= 0 ? '+' : ''}${quote.change.toStringAsFixed(2)} (${quote.changePercent >= 0 ? '+' : ''}${quote.changePercent.toStringAsFixed(2)}%)');
    print('  Day Range:      ${quote.low.toStringAsFixed(2)} - ${quote.high.toStringAsFixed(2)}');
    print('  Previous Close: ${quote.previousClose.toStringAsFixed(2)} ${quote.currency}');
    print('========================================');
  }
}

class CryptoCommand extends Command {
  @override
  final name = 'crypto';
  @override
  final description = 'Fetch a cryptocurrency spot quote.';

  @override
  void run() async {
    if (argResults?.rest.isEmpty ?? true) {
      print('Error: Specify a coin ID, e.g.: novaengine crypto bitcoin');
      exit(1);
    }
    final coinId = argResults!.rest.first;
    final gecko = CoinGeckoService();
    final quote = await gecko.getCrypto(coinId);

    if (quote == null) {
      print("Error: Cryptocurrency '$coinId' not found.");
      exit(1);
    }

    print('========================================');
    print('  CRYPTO QUOTE: ${quote.name} (${quote.symbol})');
    print('========================================');
    print('  Market Rank:    #${quote.marketCapRank}');
    print('  Spot Price:     €${quote.currentPrice.toStringAsFixed(2)}');
    print('  24h Change:     ${quote.priceChangePercentage24h >= 0 ? '+' : ''}${quote.priceChangePercentage24h.toStringAsFixed(2)}%');
    print('  Market Cap:     €${quote.marketCap.toStringAsFixed(0)}');
    print('  24h Volume:     €${quote.totalVolume.toStringAsFixed(0)}');
    print('========================================');
  }
}

class BuyCommand extends Command {
  @override
  final name = 'buy';
  @override
  final description = 'Execute a simulated buy order with statutory tax auditing.';

  BuyCommand() {
    argParser
      ..addOption('price', abbr: 'p', help: 'Explicit unit execution price.')
      ..addFlag('crypto', help: 'Treat asset as cryptocurrency.')
      ..addOption('country', abbr: 'c', defaultsTo: 'ES', help: 'Jurisdiction code.');
  }

  @override
  void run() async {
    final rest = argResults?.rest ?? [];
    if (rest.length < 2) {
      print('Usage: novaengine buy <asset> <quantity> [--price <p>] [--crypto] [--country <c>]');
      exit(1);
    }
    final assetId = rest[0];
    final quantity = double.tryParse(rest[1]);
    if (quantity == null || quantity <= 0) {
      print('Error: Invalid quantity specified.');
      exit(1);
    }

    final price = argResults?['price'] != null ? double.tryParse(argResults!['price'] as String) : null;
    final isCrypto = argResults?['crypto'] as bool? ?? false;
    final country = argResults?['country'] as String? ?? 'ES';

    final engine = NovaEngine(
      userCountry: country,
      storageProvider: JsonFileStorageProvider(),
    );
    await engine.loadFromStorage();

    final receipt = await engine.buy(
      assetId: assetId,
      quantity: quantity,
      pricePerUnit: price,
      assetType: isCrypto ? AssetClass.crypto : AssetClass.stock,
      countryCode: country,
    );

    if (receipt.status == ExecutionStatus.rejected) {
      print('Execution Rejected: ${receipt.rejectionReason}');
      exit(1);
    }

    final profile = TaxService.getProfile(country);
    print('========================================');
    print('  ORDER EXECUTED: BUY ${receipt.quantity} ${receipt.assetId}');
    print('========================================');
    print('  Receipt ID:       ${receipt.id}');
    print('  Asset Name:       ${receipt.assetName}');
    print('  Unit Price:       ${profile.currencySymbol}${receipt.pricePerUnit.toStringAsFixed(2)}');
    print('  Gross Amount:     ${profile.currencySymbol}${receipt.totalGrossAmount.toStringAsFixed(2)}');
    print('  Broker Fee:       ${profile.currencySymbol}${receipt.brokerFee.toStringAsFixed(2)}');
    print('  Transaction Tax:  ${profile.currencySymbol}${receipt.transactionTax.toStringAsFixed(2)}');
    print('  Settled Outlay:   ${profile.currencySymbol}${receipt.netAmount.toStringAsFixed(2)}');
    print('  Cash Remaining:   €${engine.cashBalance.toStringAsFixed(2)}');
    print('========================================');
  }
}

class SellCommand extends Command {
  @override
  final name = 'sell';
  @override
  final description = 'Execute a simulated sell order with capital gains withholding.';

  SellCommand() {
    argParser
      ..addOption('price', abbr: 'p', help: 'Explicit unit execution price.')
      ..addFlag('crypto', help: 'Treat asset as cryptocurrency.')
      ..addOption('country', abbr: 'c', defaultsTo: 'ES', help: 'Jurisdiction code.');
  }

  @override
  void run() async {
    final rest = argResults?.rest ?? [];
    if (rest.length < 2) {
      print('Usage: novaengine sell <asset> <quantity> [--price <p>] [--crypto] [--country <c>]');
      exit(1);
    }
    final assetId = rest[0];
    final quantity = double.tryParse(rest[1]);
    if (quantity == null || quantity <= 0) {
      print('Error: Invalid quantity specified.');
      exit(1);
    }

    final price = argResults?['price'] != null ? double.tryParse(argResults!['price'] as String) : null;
    final isCrypto = argResults?['crypto'] as bool? ?? false;
    final country = argResults?['country'] as String? ?? 'ES';

    final engine = NovaEngine(
      userCountry: country,
      storageProvider: JsonFileStorageProvider(),
    );
    await engine.loadFromStorage();

    final receipt = await engine.sell(
      assetId: assetId,
      quantity: quantity,
      pricePerUnit: price,
      assetType: isCrypto ? AssetClass.crypto : AssetClass.stock,
      countryCode: country,
    );

    if (receipt.status == ExecutionStatus.rejected) {
      print('Execution Rejected: ${receipt.rejectionReason}');
      exit(1);
    }

    final profile = TaxService.getProfile(country);
    print('========================================');
    print('  ORDER EXECUTED: SELL ${receipt.quantity} ${receipt.assetId}');
    print('========================================');
    print('  Receipt ID:         ${receipt.id}');
    print('  Asset Name:         ${receipt.assetName}');
    print('  Execution Price:    ${profile.currencySymbol}${receipt.pricePerUnit.toStringAsFixed(2)}');
    print('  Gross Proceeds:     ${profile.currencySymbol}${receipt.totalGrossAmount.toStringAsFixed(2)}');
    print('  Broker Commission:  ${profile.currencySymbol}${receipt.brokerFee.toStringAsFixed(2)}');
    print('  Capital Gains Tax:  ${profile.currencySymbol}${receipt.capitalGainsTax.toStringAsFixed(2)}');
    print('  Net Cash Credited:  ${profile.currencySymbol}${receipt.netAmount.toStringAsFixed(2)}');
    print('  Updated Balance:    €${engine.cashBalance.toStringAsFixed(2)}');
    print('========================================');
  }
}

class StatementCommand extends Command {
  @override
  final name = 'statement';
  @override
  final description = 'Print portfolio valuation statement and open positions.';

  StatementCommand() {
    argParser
      ..addOption('country', abbr: 'c', defaultsTo: 'ES', help: 'Country tax code.')
      ..addOption('currency', help: 'Display currency override.');
  }

  @override
  void run() async {
    final country = argResults?['country'] as String? ?? 'ES';
    final currency = argResults?['currency'] as String?;

    final engine = NovaEngine(
      userCountry: country,
      storageProvider: JsonFileStorageProvider(),
    );
    await engine.loadFromStorage();
    final statement = engine.getStatement(currencyCode: currency);

    final sym = statement['currency_symbol'] as String;
    print('========================================');
    print('  PORTFOLIO STATEMENT (${statement['currency']})');
    print('========================================');
    print('  Cash Reserves:    $sym${(statement['cash_balance'] as double).toStringAsFixed(2)}');
    print('  Invested Equity:  $sym${(statement['invested_value'] as double).toStringAsFixed(2)}');
    print('  Total Net Worth:  $sym${(statement['total_net_worth'] as double).toStringAsFixed(2)}');
    print('  Total Return:     $sym${(statement['total_profit_loss'] as double).toStringAsFixed(2)} (${(statement['total_profit_loss_pct'] as double).toStringAsFixed(2)}%)');
    print('----------------------------------------');

    final holdings = statement['holdings'] as List<dynamic>;
    if (holdings.isEmpty) {
      print('  No open positions in ledger.');
    } else {
      print('  OPEN POSITIONS:');
      for (final h in holdings) {
        final item = h as Map<String, dynamic>;
        print('  - ${item['asset_id']} (${item['name']}): Qty: ${item['quantity']} | Avg: $sym${(item['avg_buy_price'] as double).toStringAsFixed(2)} | Current: $sym${(item['current_price'] as double).toStringAsFixed(2)} | P&L: $sym${(item['profit_loss'] as double).toStringAsFixed(2)} (${(item['profit_loss_pct'] as double).toStringAsFixed(2)}%)');
      }
    }
    print('========================================');
  }
}

class TaxesCommand extends Command {
  @override
  final name = 'taxes';
  @override
  final description = 'List statutory tax parameters across supported jurisdictions.';

  @override
  void run() {
    print('========================================================================');
    print('  SUPPORTED NATIONAL FISCAL REGIMES');
    print('========================================================================');
    for (final p in TaxService.supportedCountries) {
      print('  [${p.code}] ${p.name.padRight(16)} | FTT: ${(p.stockTransactionTaxRate * 100).toStringAsFixed(2)}% | CGT: ${(p.capitalGainsTaxRate * 100).toStringAsFixed(2)}% | Broker: ${(p.brokerFeeRate * 100).toStringAsFixed(2)}% (min ${p.currencySymbol}${p.minimumBrokerFee.toStringAsFixed(2)})');
      print('       Tax Authority: ${p.taxAuthority}');
    }
    print('========================================================================');
  }
}
