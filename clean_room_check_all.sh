#!/bin/bash
echo "Building workspaces..."
npm run build --workspaces

echo "Setting up clean room..."
mkdir -p /tmp/clean-room-all
cd /tmp/clean-room-all
npm init -y >/dev/null

echo "Packing and testing all packages..."
cd /Users/sumitg/Projects/fde-lab

for pkg_dir in packages/*; do
  if [ -d "$pkg_dir" ]; then
    pkg_name=$(basename "$pkg_dir")
    cd "$pkg_dir"
    tarball=$(npm pack)
    mv "$tarball" /tmp/clean-room-all/
    cd /Users/sumitg/Projects/fde-lab
  fi
done

cd /tmp/clean-room-all
for tarball in *.tgz; do
  npm install "./$tarball" >/dev/null
done

failed=0

for pkg_dir in /Users/sumitg/Projects/fde-lab/packages/*; do
  if [ -d "$pkg_dir" ]; then
    pkg_name=$(basename "$pkg_dir")
    if [ "$pkg_name" != "cli-core" ]; then
      
      bin_name=$(node -e "const pkg=require('$pkg_dir/package.json'); if(pkg.bin) console.log(Object.keys(pkg.bin)[0]); else console.log('');")
      
      if [ -z "$bin_name" ]; then
        echo "No bin found for $pkg_name"
        continue
      fi

      echo "Testing $bin_name --manifest..."
      npx "$bin_name" --manifest > manifest.json
      if ! python3 -m json.tool manifest.json >/dev/null; then
         echo "FAIL JSON manifest $bin_name"
         failed=1
      fi
      
      echo "Testing $bin_name --json..."
      npx "$bin_name" --json > result.json
      if ! python3 -m json.tool result.json >/dev/null; then
         echo "FAIL JSON result $bin_name"
         failed=1
      fi
    fi
  fi
done

if [ "$failed" -eq 1 ]; then
   echo "CLEAN ROOM CHECKS FAILED"
   exit 1
else
   echo "ALL CLEAN ROOM CHECKS PASSED"
fi
