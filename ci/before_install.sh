openssl aes-256-cbc -K $encrypted_68d9c3eaf1da_key -iv $encrypted_68d9c3eaf1da_iv -in travis.enc -out travis -d
chmod 600 ./travis
eval "$(ssh-agent -s)"
ssh-add travis
# On the windows builder, we don't have any python3 and we need some.
if [ "$TRAVIS_OS_NAME" = "windows" ]
then
choco install -y python3 --params "/InstallDir:C:\\Python"
export PATH="/c/Python:/c/Python/Scripts:$PATH"
python -m pip install --upgrade pip wheel
# Because of a pyinstaller bug, we currently need a dev version.
pip install https://github.com/pyinstaller/pyinstaller/tarball/develop
fi