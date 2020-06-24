VERSION="1.2.0"

# To build a release build for Windows you need also: pyintallar, upx,
# ImageMagick and 7zip install and accessible via the users or systems path
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
        7z a bassieracing-$VERSION-win64.zip bassieracing-$VERSION-win64
        cd ..

        rm -r build bassieracing.spec
    fi

    rm icon.ico

# To render a class diagram you need pyreverse (pylint) and graphviz
# installed and accessible via the users or systems path
elif [ "$1" == "render" ]; then
    pyreverse -o pdf -p bassieracing $(find src -name *.py)
    mv classes_bassieracing.pdf docs/class-diagram.pdf
    rm packages_bassieracing.pdf

# When no release just run the python file
else
    # Change this line to "python3 src/main.py" on Ubuntu 18.04 or lower!
    python src/main.py
fi
