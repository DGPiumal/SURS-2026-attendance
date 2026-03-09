import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const SursScannerApp());
}

class SursScannerApp extends StatelessWidget {
  const SursScannerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SURS 2026 Scanner',
      theme: ThemeData(
        // SURS Brand Colors
        primaryColor: const Color(0xFF6B2B2C), // Faculty Maroon
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6B2B2C),
          primary: const Color(0xFF6B2B2C),
          secondary: const Color(0xFFADD8E6), // Light blue from the website
        ),
        useMaterial3: true,
      ),
      home: const ScannerScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  final MobileScannerController cameraController = MobileScannerController();
  bool isScanning = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black, // Dark background behind the camera
      appBar: AppBar(
        backgroundColor: const Color(0xFF6B2B2C), // SURS Maroon
        iconTheme: const IconThemeData(color: Colors.white),
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'SURS 2026 Scanner',
              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20),
            ),
            Text(
              'Faculty of Science, UoP',
              style: TextStyle(color: Colors.white70, fontSize: 13),
            ),
          ],
        ),
        actions: [
          ValueListenableBuilder(
            valueListenable: cameraController,
            builder: (context, state, child) {
              switch (state.torchState) {
                case TorchState.on:
                  return IconButton(
                    icon: const Icon(Icons.flash_on, color: Colors.amber),
                    iconSize: 28.0,
                    onPressed: () => cameraController.toggleTorch(),
                  );
                case TorchState.off:
                default:
                  return IconButton(
                    icon: const Icon(Icons.flash_off, color: Colors.white),
                    iconSize: 28.0,
                    onPressed: () => cameraController.toggleTorch(),
                  );
              }
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          // 1. The Camera Feed
          MobileScanner(
            controller: cameraController,
            onDetect: (capture) {
              if (!isScanning) return;

              final List<Barcode> barcodes = capture.barcodes;
              for (final barcode in barcodes) {
                if (barcode.rawValue != null) {
                  final String scannedEmail = barcode.rawValue!;
                  setState(() => isScanning = false);
                  _sendToBackend(scannedEmail);
                }
              }
            },
          ),
          
          // 2. The Targeting Frame (SURS Light Blue)
          Center(
            child: Container(
              width: 280,
              height: 280,
              decoration: BoxDecoration(
                border: Border.all(color: const Color(0xFFADD8E6), width: 4.0), // Light blue from website
                borderRadius: BorderRadius.circular(24.0),
                boxShadow: const [
                  BoxShadow(color: Colors.black26, blurRadius: 20, spreadRadius: 5)
                ],
              ),
            ),
          ),

          // 3. Bottom Branding Banner
          Positioned(
            bottom: 40,
            left: 0,
            right: 0,
            child: Column(
              children: [
                const Text(
                  "Align QR Code within the frame",
                  style: TextStyle(
                    color: Colors.white, 
                    fontSize: 16, 
                    fontWeight: FontWeight.w500,
                    shadows: [Shadow(color: Colors.black, blurRadius: 10)]
                  ),
                ),
                const SizedBox(height: 15),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF6B2B2C).withOpacity(0.95), // Transparent Maroon
                    borderRadius: BorderRadius.circular(30),
                    border: Border.all(color: const Color(0xFFADD8E6).withOpacity(0.5), width: 1),
                  ),
                  child: const Text(
                    "Symposium Date: 26th March 2026",
                    style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // --- Backend Communication Logic ---
  Future<void> _sendToBackend(String email) async {
    // ⚠️ I put your last known IP address here. Change it if your Wi-Fi resets!
    final String apiUrl = 'http://192.168.1.101:8000/scan';

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Syncing $email...', style: const TextStyle(color: Colors.white)),
        backgroundColor: const Color(0xFF6B2B2C),
        duration: const Duration(seconds: 1)
      ),
    );

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'surs_mail': email,
          'device_id': 'huawei_scanner_1'
        }),
      );

      if (response.statusCode == 200) {
        final responseData = jsonDecode(response.body);

        if (responseData['status'] == 'success') {
          _showScanResult('✅ Check-in Successful', responseData['message'], Colors.green);
        } else if (responseData['status'] == 'duplicate') {
          _showScanResult('⚠️ Already Scanned', responseData['message'], Colors.orange);
        }
      } else {
        _showScanResult('❌ Server Error', 'Code: ${response.statusCode}', Colors.red);
      }
    } catch (e) {
      _showScanResult('⚠️ Offline/Error', 'Could not reach server. Check Wi-Fi.', Colors.red);
    }
  }

  void _showScanResult(String title, String message, Color titleColor) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          title: Text(title, style: TextStyle(color: titleColor, fontWeight: FontWeight.bold)),
          content: Text(message, style: const TextStyle(fontSize: 16)),
          actions: [
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF6B2B2C),
                foregroundColor: Colors.white,
              ),
              onPressed: () {
                Navigator.pop(context);
                Future.delayed(const Duration(seconds: 1), () {
                  setState(() => isScanning = true);
                });
              },
              child: const Text('Next Student'),
            ),
          ],
        );
      },
    );
  }
}