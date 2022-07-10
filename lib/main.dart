import 'package:flutter/material.dart';
import 'package:scan/scan.dart';
import 'package:http/http.dart' as http;
import 'dart:convert' show jsonDecode;

import 'dart:developer';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Collection Scanner',
      theme: ThemeData(
        // This is the theme of your application.
        //
        // Try running your application with "flutter run". You'll see the
        // application has a blue toolbar. Then, without quitting the app, try
        // changing the primarySwatch below to Colors.green and then invoke
        // "hot reload" (press "r" in the console where you ran "flutter run",
        // or simply save your changes to "hot reload" in a Flutter IDE).
        // Notice that the counter didn't reset back to zero; the application
        // is not restarted.
        primarySwatch: Colors.blue,
      ),
      home: const MyHomePage(title: 'Collection Scanner Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({Key? key, required this.title}) : super(key: key);

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  ScanController controller = ScanController();
  String _scanResult = '';
  String _bookName = '';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text(
              'You Barcode Contains the Text:',
            ),
            Text(
              _scanResult,
              style: Theme.of(context).textTheme.headline4,
            ),
            const Text(
              'The book is:',
            ),
            Text(
              _bookName,
              style: Theme.of(context).textTheme.headline4,
            )
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showBarcodeScanner,
        tooltip: 'Scan Barcode',
        child: const Icon(
          Icons.scanner,
          color: Colors.white
        ),
      ), // This trailing comma makes auto-formatting nicer for build methods.
    );
  }

  _showBarcodeScanner() {
    setState(() {
      _bookName = '';
      _scanResult = '';
    });

    return showModalBottomSheet(
      isScrollControlled: true,
      context: context,
      builder: (builder) {
        return StatefulBuilder(builder: (BuildContext context, setState) {
          return SizedBox(
              height: MediaQuery.of(context).size.height / 2,
              child: Scaffold(
                appBar: _buildBarcodeScannerAppBar(),
                body: _buildBarcodeScannerBody(),
              ));
        });
      },
    );
  }

  AppBar _buildBarcodeScannerAppBar() {
    return AppBar(
      bottom: PreferredSize(
        preferredSize: const Size.fromHeight(4.0),
        child: Container(color: Colors.purpleAccent, height: 4.0),
      ),
      title: const Text('Scan Your Barcode'),
      elevation: 0.0,
      backgroundColor: const Color(0xFF333333),
      leading: GestureDetector(
        onTap: () => Navigator.of(context).pop(),
        child: const Center(
            child: Icon(
              Icons.cancel,
              color: Colors.white,
            )),
      ),
      actions: [
        Container(
            alignment: Alignment.center,
            padding: const EdgeInsets.only(right: 16.0),
            child: GestureDetector(
                onTap: () => controller.toggleTorchMode(),
                child: const Icon(Icons.flashlight_on))),
      ],
    );
  }

  Widget _buildBarcodeScannerBody() {
    return SizedBox(
      height: 400,
      child: ScanView(
        controller: controller,
        scanAreaScale: .7,
        scanLineColor: Colors.purpleAccent,
        onCapture: (data) {
          setState(() {
            _scanResult = data;
            sendISBN(data);
            Navigator.of(context).pop();
          });
        },
      ),
    );
  }

  // Future<http.Response> sendISBN(String isbn) async {
  void sendISBN(String isbn) async {
    log('data: $isbn');  // DEBUG FIXME

    final response = await http.get(
      Uri.parse('http://192.168.1.14:4100/books/$isbn'),
      headers: <String , String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
    );
    log('result fetched');

    if (response.statusCode == 200) {
      updateBookNameVariable(jsonDecode(response.body));
    }
  }

  void updateBookNameVariable(responseBody) {
    switch (responseBody["status_code"]) {
      case 200 : // Enter this block if mark == 0
        setState(() {
          _bookName = responseBody["title"];
        });
        break;
      case 401: // Enter this block if mark == 1 or mark == 2 or mark == 3
        setState(() {
          _bookName = responseBody["message"];
        });
        break;
      case 404: // Enter this block if mark == 1 or mark == 2 or mark == 3
        setState(() {
          _bookName = responseBody["message"];
        });
        break;
      default :
        setState(() {
          _bookName = "Error";
        });
        break;
    }
  }
}
