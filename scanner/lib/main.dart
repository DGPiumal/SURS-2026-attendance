import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:http/http.dart' as http;
import 'package:haptic_feedback/haptic_feedback.dart'; // Haptic feedback for scan results
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
        // UoP Official Colors (Maroon & Gold)
        primaryColor: const Color(0xFF800000), 
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF800000),
          primary: const Color(0xFF800000),
          secondary: const Color(0xFFFFD700), // UoP Gold
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
  
  // UI state used for feedback after each scan.
  int localScanCount = 0;
  String lastScannedStudent = "Waiting for first scan...";
  Color lastScanColor = Colors.grey;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black, 
      appBar: AppBar(
        backgroundColor: const Color(0xFF800000), // UoP Maroon
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'SURS 2026 | UoP',
              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20),
            ),
            // The Live Local Counter!
            Text(
              'My Scans Today: $localScanCount',
              style: const TextStyle(color: Color(0xFFFFD700), fontSize: 13, fontWeight: FontWeight.w600), // UoP Gold
            ),
          ],
        ),
        actions: [
          // Flashlight Toggle
          ValueListenableBuilder(
            valueListenable: cameraController,
            builder: (context, state, child) {
              final isOn = state.torchState == TorchState.on;
              return IconButton(
                icon: Icon(isOn ? Icons.flash_on : Icons.flash_off, color: isOn ? const Color(0xFFFFD700) : Colors.white),
                iconSize: 28.0,
                onPressed: () => cameraController.toggleTorch(),
              );
            },
          ),
          const SizedBox(width: 10),
        ],
      ),
      body: Stack(
        children: [
          // Camera view: detects barcodes and sends the first valid scan to the backend.
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

          // Visual targeting frame to help align the QR code.
          Center(
            child: Container(
              width: 280,
              height: 280,
              decoration: BoxDecoration(
                border: Border.all(color: const Color(0xFFFFD700), width: 4.0),
                borderRadius: BorderRadius.circular(24.0),
                boxShadow: const [
                  BoxShadow(color: Colors.black45, blurRadius: 20, spreadRadius: 5)
                ],
              ),
            ),
          ),

          // 3. The "Last Scanned" Memory Card
          Positioned(
            bottom: 40,
            left: 20,
            right: 20,
            child: Container(
              padding: const EdgeInsets.all(15),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(15),
                border: Border.all(color: lastScanColor, width: 3),
                boxShadow: const [BoxShadow(color: Colors.black54, blurRadius: 10, offset: Offset(0, 5))],
              ),
              child: Column(
                children: [
                  Text(
                    "Last Scanned:",
                    style: TextStyle(color: Colors.grey[700], fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    lastScannedStudent,
                    style: TextStyle(color: lastScanColor, fontSize: 18, fontWeight: FontWeight.bold),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // --- Backend Communication Logic ---
  Future<void> _sendToBackend(String email) async {
// Update this URL to the backend server address reachable from the device.
  // For local testing, use the machine's local network IP (not localhost).
    final String apiUrl = 'http://10.30.36.122:8000/scan';

    // Immediate Light Vibration so the volunteer knows the camera saw the QR code
    await Haptics.vibrate(HapticsType.light);

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
          // Successful scan: update UI and provide positive haptic feedback.
          await Haptics.vibrate(HapticsType.success);
          setState(() {
            localScanCount++;
            lastScannedStudent = "✅ $email\n(Approved)";
            lastScanColor = Colors.green;
          });
          _showScanResult('✅ Access Granted', '$email recorded successfully.', Colors.green);

        } else if (responseData['status'] == 'duplicate') {
          // Duplicate scan: inform the user and keep the UI in warning state.
          await Haptics.vibrate(HapticsType.warning);
          setState(() {
            lastScannedStudent = "⚠️ $email\n(Already Scanned!)";
            lastScanColor = Colors.orange;
          });
          _showScanResult('⚠️ Duplicate Scan', '$email has already checked in today.', Colors.orange);
        }
      } else {
        // Backend returned a non-200 status code.
        await Haptics.vibrate(HapticsType.error);
        _showScanResult('❌ Server Error', 'Code: ${response.statusCode}', Colors.red);
      }
    } catch (e) {
      // Network error or other exception.
      await Haptics.vibrate(HapticsType.error);
      _showScanResult('📶 Connection Failed', 'Could not reach server. Check Wi-Fi.', Colors.red);
    }
  }

  void _showScanResult(String title, String message, Color color) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20), side: BorderSide(color: color, width: 2)),
          title: Text(title, style: TextStyle(color: color, fontWeight: FontWeight.bold)),
          content: Text(message, style: const TextStyle(fontSize: 16)),
          actions: [
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: color,
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 50), // Big easy-to-tap button
              ),
              onPressed: () {
                Navigator.pop(context);
                // Wait half a second before allowing the next scan to prevent accidental double-scans
                Future.delayed(const Duration(milliseconds: 500), () {
                  setState(() => isScanning = true);
                });
              },
              child: const Text('SCAN NEXT STUDENT', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            ),
          ],
        );
      },
    );
  }
}