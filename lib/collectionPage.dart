import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert' show jsonDecode, jsonEncode;
import 'dart:async';

import 'dart:developer';

Future<Collection> fetchCollection() async {
  final response = await http.get(
    Uri.parse('http://192.168.1.14:4100/books'),
    headers: <String , String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
  );

  if (response.statusCode == 200) {
    return Collection.fromJson(jsonDecode(response.body));
  } else {
    throw Exception('Failed to load collection');
  }
}

class Collection {
  final List collection;
  final List columns;

  const Collection({
    required this.collection,
    required this.columns,
  });

  factory Collection.fromJson(Map<String, dynamic> json) {
    return Collection(
      collection: json['collection']['data'],
      columns: json['collection']['columns'],
    );
  }
}

class CollectionPage extends StatefulWidget {
  final String title;

  const CollectionPage({super.key, required this.title});

  @override
  State<CollectionPage> createState() => _CollectionPageState();
}

class _CollectionPageState extends State<CollectionPage> {
  late Future<Collection> futureCollection;

  @override
  void initState() {
    super.initState();
    futureCollection = fetchCollection();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: widget.title,
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: Scaffold(
        appBar: AppBar(title: Text(widget.title)),
        body: Center(
          child:  FutureBuilder<Collection> (
            future: futureCollection,
            builder: (context, snapshot) {
              if (snapshot.hasData) {
                // print(jsonEncode(snapshot.data!));
                var collection = snapshot.data!.collection;

                return ListView.builder(
                  // Let the ListView know how many items it needs to build.
                  itemCount: collection.length,
                  // Provide a builder function. This is where the magic happens.
                  // Convert each item into a widget based on the type of item it is.
                  itemBuilder: (context, index) {
                    final item = collection[index];
                    final isbn = item[0];
                    final title = item[1];

                    return ListTile(
                        leading: const Icon(Icons.book),
                        title: Text(title),
                        subtitle: Text('$isbn')
                    );
                  },
                );
                // return Text(snapshot.data!.columns[0]);
              } else if (snapshot.hasError) {
                return Text('${snapshot.error}');
              }

              return const CircularProgressIndicator();
            },
          ),
        )
      )
    );
  }
}
