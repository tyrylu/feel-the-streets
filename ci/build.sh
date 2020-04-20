cargo build --verbose --release --all
cargo build --verbose --all
# On Windows, build the executable binary.
if [ "$TRAVIS_OS_NAME" = "windows" ]
then
python -m pip install --upgrade pip wheel setuptools
# Because of a pyinstaller bug, we currently need a dev version.
python -m pip install https://github.com/pyinstaller/pyinstaller/tarball/develop
# Install the requirements
python -m pip install -r app_requirements.txt
# We need osm_db module in the right place.
mv target/release/osm_db.dll osm_db.pyd
# And now build the executable
pyinstaller run_app.spec
# We don't need some of the Qt libraries.
rm dist/fts/{Qt5Quick.dll,Qt5QmlModels.dll,Qt5VirtualKeyboard.dll}
fi