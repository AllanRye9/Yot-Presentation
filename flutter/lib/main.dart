import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'screens/upload_screen.dart';
import 'screens/settings_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final serverUrl = prefs.getString('server_url') ?? 'http://localhost:5000';
  final voiceLocale = prefs.getString('voice_locale') ?? 'en_US';
  runApp(YotApp(initialServerUrl: serverUrl, initialVoiceLocale: voiceLocale));
}

class YotApp extends StatefulWidget {
  final String initialServerUrl;
  final String initialVoiceLocale;

  const YotApp({
    super.key,
    required this.initialServerUrl,
    required this.initialVoiceLocale,
  });

  @override
  State<YotApp> createState() => _YotAppState();
}

class _YotAppState extends State<YotApp> {
  late String _serverUrl;
  late String _voiceLocale;

  @override
  void initState() {
    super.initState();
    _serverUrl = widget.initialServerUrl;
    _voiceLocale = widget.initialVoiceLocale;
  }

  void _updateServerUrl(String url) {
    setState(() => _serverUrl = url);
  }

  Future<void> _reloadPreferences() async {
    final prefs = await SharedPreferences.getInstance();
    if (mounted) {
      setState(() {
        _serverUrl = prefs.getString('server_url') ?? _serverUrl;
        _voiceLocale = prefs.getString('voice_locale') ?? _voiceLocale;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Yot-Presentation',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6C63FF),
          brightness: Brightness.dark,
        ),
        useMaterial3: true,
        fontFamily: 'Roboto',
      ),
      home: UploadScreen(
        serverUrl: _serverUrl,
        voiceLocale: _voiceLocale,
        onSettingsTap: () async {
          await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => SettingsScreen(
                serverUrl: _serverUrl,
                onServerUrlChanged: _updateServerUrl,
              ),
            ),
          );
          // Reload locale preference after returning from settings
          await _reloadPreferences();
        },
      ),
    );
  }
}
