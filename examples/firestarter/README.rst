===================================
Deploy pyramid app with firestarter
===================================


configure::

  $ cd ./../..
  $ tox -e example_firestarter
  $ cd example/firestarter

run::

  $ RUST_LOG=debug /path/to/firestarter run --config firestarter.toml
