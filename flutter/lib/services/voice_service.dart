import 'package:speech_to_text/speech_to_text.dart' as stt;

typedef OnResult = void Function(String transcript);
typedef OnStatusChange = void Function(bool isListening);

/// Wraps [SpeechToText] and provides a simple start/stop API.
class VoiceService {
  final stt.SpeechToText _speech = stt.SpeechToText();
  bool _available = false;

  Future<bool> initialize() async {
    _available = await _speech.initialize(
      onError: (error) {},
      onStatus: (_) {},
    );
    return _available;
  }

  bool get isAvailable => _available;
  bool get isListening => _speech.isListening;

  Future<void> startListening({
    required OnResult onResult,
    required OnStatusChange onStatusChange,
    String localeId = 'en_US',
  }) async {
    if (!_available) return;
    onStatusChange(true);
    await _speech.listen(
      onResult: (result) {
        if (result.finalResult) {
          onStatusChange(false);
          onResult(result.recognizedWords);
        }
      },
      localeId: localeId,
      listenFor: const Duration(seconds: 10),
      pauseFor: const Duration(seconds: 3),
      cancelOnError: true,
    );
  }

  Future<void> stopListening({required OnStatusChange onStatusChange}) async {
    await _speech.stop();
    onStatusChange(false);
  }

  Future<List<String>> availableLocales() async {
    final locales = await _speech.locales();
    return locales.map((l) => l.localeId).toList();
  }
}
