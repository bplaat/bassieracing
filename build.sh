VERSION="1.0.1"

# To build a release build for Windows you need also: pyintallar, upx,
# ImageMagick and 7zip install and accesable via the path
if [ "$1" == "release" ]; then
    # Remove old dist folder
    rm -r dist

    # Convert PNG icon to ICO for Windows Executable
    magick convert assets/images/icon.png -define icon:auto-resize="16,24,32,48,64,96,128,256" icon.ico

    # Pack to app with pyinstaller
    if pyinstaller --upx-exclude=vcruntime140.dll --hidden-import=pkg_resources.py2_warn \
        -F --add-data="C:\Users\bplaat\AppData\Local\Programs\Python\Python38\Lib\site-packages\pygame\libmpg123.dll;." \
        -n bassieracing -i icon.ico -w src/main.py
    then
        # Move executable and assets to right folder
        mkdir dist/bassieracing-$VERSION-win64
        mv dist/bassieracing.exe dist/bassieracing-$VERSION-win64
        cp -R assets dist/bassieracing-$VERSION-win64
        rm -R dist/bassieracing-$VERSION-win64/assets/maps/custom

        # Zip the dist folder
        cd dist
        7z a bassieracing-1.0.0-win64.zip bassieracing-$VERSION-win64
        cd ..

        rm -r build bassieracing.spec
    fi

    rm icon.ico

# When no release just run the python file
else
    python src/main.py
fi
