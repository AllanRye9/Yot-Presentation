import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'screens/upload_screen.dart';
import 'screens/settings_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final serverUrl = prefs.getString('server_url') ?? 'http://localhost:5000';
  runApp(YotApp(initialServerUrl: serverUrl));
}

class YotApp extends StatefulWidget {
  final String initialServerUrl;
  const YotApp({super.key, required this.initialServerUrl});

  @override
  State<YotApp> createState() => _YotAppState();
}

class _YotAppState extends State<YotApp> {
  late String _serverUrl;

  @override
  void initState() {
    super.initState();
    _serverUrl = widget.initialServerUrl;
  }

  void _updateServerUrl(String url) {
    setState(() => _serverUrl = url);
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
        onSettingsTap: () => Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => SettingsScreen(
              serverUrl: _serverUrl,
              onServerUrlChanged: _updateServerUrl,
            ),
          ),
        ),
      ),
    );
  }
}
