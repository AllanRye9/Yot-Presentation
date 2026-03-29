import 'package:flutter/material.dart';

/// Animated microphone button used on the presentation screen.
class VoiceButton extends StatelessWidget {
  final bool listening;
  final VoidCallback onTap;

  const VoiceButton({super.key, required this.listening, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        width: 64,
        height: 64,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: listening ? cs.error : cs.primary,
          boxShadow: listening
              ? [
                  BoxShadow(
                    color: cs.error.withOpacity(0.5),
                    blurRadius: 16,
                    spreadRadius: 4,
                  )
                ]
              : [],
        ),
        child: Icon(
          listening ? Icons.mic : Icons.mic_none,
          color: Colors.white,
          size: 28,
        ),
      ),
    );
  }
}
