# sqlitemap

An attempt at replicating much of the HashMap interface and trait
implementations but using sqlite as a backend instead.  Just uses rusqlite and
depends on its traits as much as possible, using its ToSql and FromSql traits to
insert and retrieve any objects.  This means that most checking is done at
runtime, unfortunately, because Rust can't know at compile time if the object
being pulled is deserializable or not.  Results have to wrap most database
operations to bubble sql and database errors, so many retrieval functions are an
Option within a result.
