Book App
===

The purpose of this project is to create a quick book collection mobile app :
1. Read a barcode
2. Find the corresponding book
3. Add it to your numerical library
4. Make fun with your library:
  1. Share it
  2. Organize it
  3. Create booklist
  4. Create wishlist (books found at a retailer that you would like)
  5. Review your books

> It can be interesting to link it with Notion to publish your reviews / lists


## Documentation

- [mobile development using Python](https://realpython.com/mobile-app-kivy-python/)
- [Barcode reading using Python](https://www.geeksforgeeks.org/how-to-make-a-barcode-reader-in-python/)
- [Google book API](https://developers.google.com/books/docs/v1/using) ([example with *Eden*'s ISBN](https://www.googleapis.com/books/v1/volumes?q=9782809495454))



## Stack

- Python or Flutter or Go or React Native (TS)
- SQLite


```markdown
To run your project, run one of the following yarn commands.

- yarn start # you can open iOS, Android, or web from here, or run them directly with the commands below.
- yarn android
- yarn ios # requires an iOS device or macOS for access to an iOS simulator
- yarn web
```

---

## Quick run

Server
```shell
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 4100
```


---
Thibault *Santonja*<br/>
*2021*
