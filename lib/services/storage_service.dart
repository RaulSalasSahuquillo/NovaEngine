import 'dart:convert';
import 'dart:io';
import '../models/portfolio_item.dart';
import '../models/transaction.dart';

/// Storage provider contract for persisting engine state.
abstract class StorageProvider {
  Future<bool> saveState({
    required double cashBalance,
    required double initialCapital,
    required List<PortfolioItem> holdings,
    required List<Transaction> transactions,
  });

  Future<Map<String, dynamic>?> loadState();
}

/// Atomic file-based JSON persistence provider.
class JsonFileStorageProvider implements StorageProvider {
  final File file;

  JsonFileStorageProvider({String filePath = 'portfolio_state.json'})
      : file = File(filePath);

  @override
  Future<bool> saveState({
    required double cashBalance,
    required double initialCapital,
    required List<PortfolioItem> holdings,
    required List<Transaction> transactions,
  }) async {
    final tempFile = File('${file.path}.tmp');
    try {
      final payload = {
        'cash_balance': cashBalance,
        'initial_capital': initialCapital,
        'positions': holdings.map((h) => h.toJson()).toList(),
        'transactions': transactions.map((t) => t.toJson()).toList(),
      };
      await tempFile.writeAsString(json.encode(payload), flush: true);
      await tempFile.rename(file.path);
      return true;
    } catch (_) {
      if (await tempFile.exists()) {
        try {
          await tempFile.delete();
        } catch (_) {}
      }
      return false;
    }
  }

  @override
  Future<Map<String, dynamic>?> loadState() async {
    try {
      if (!await file.exists()) return null;
      final content = await file.readAsString();
      return json.decode(content) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }
}
