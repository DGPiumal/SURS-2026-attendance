import 'package:flutter_test/flutter_test.dart';
import 'package:scanner/main.dart';

void main() {
  testWidgets('App loads smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const SursScannerApp());

    // Verify that our custom app bar title exists
    expect(find.text('Scan Student QR'), findsOneWidget);
  });
}