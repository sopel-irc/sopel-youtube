#!/bin/sh
# Runs through the steps to release a version. This is only useful to the
# people with permissions to do so, of course.
set -e
cd $(dirname $0)/..

version=$(python -c "import sopel_modules.youtube as y; print(y.__version__)")
echo "Releasing version $version."

echo "PyPI username:"
read pypi_user
echo "PyPI password:"
read pypi_pass

cat <<EOF > ~/.pypirc
[distutils]
index-servers =
    pypi

[pypi]
username:$pypi_user
password:$pypi_pass
EOF

echo "Building package and uploading to PyPI..."
./setup.py sdist upload --sign
rm ~/.pypirc

echo "Done!"
