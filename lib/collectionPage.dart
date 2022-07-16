import 'dart:ffi';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert' show jsonDecode;

class CollectionPage extends StatefulWidget {
  const CollectionPage({Key? key, required this.title}) : super(key: key);

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  final String title;

  @override
  State<CollectionPage> createState() => _CollectionPageState();
}

class _CollectionPageState extends State<CollectionPage> {
  Future<List> _collection = [] as Future<List>;

  @override
  Widget build(BuildContext context) {
    setState(() {
      _collection = getCollection();
    });

    return Scaffold(
      appBar: AppBar(title: Text(widget.title)),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const <Widget>[
            Text('Your library'),
          ],
        ),
      ),
    );
  }

  Future<List> getCollection() async {
    final response = await http.get(
      Uri.parse('http://192.168.1.14:4100/books'),
      headers: <String , String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
    );

    return [response.body]; //jsonDecode(response.body);
  }
}