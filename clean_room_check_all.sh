#!/bin/bash
set -e

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
    
    # Exclude cli-core from running, but include it in install if needed?
    # Actually, the workers depend on cli-core, so we might need to pack cli-core too and install it, or it will pull from npm registry.
    # To be fully offline/local, we would pack cli-core. But let's let npm resolve from npmjs for cli-core, or just pack it.
    echo "Packing $pkg_name..."
    cd "$pkg_dir"
    tarball=$(npm pack)
    mv "$tarball" /tmp/clean-room-all/
    cd /Users/sumitg/Projects/fde-lab
  fi
done

cd /tmp/clean-room-all
for tarball in *.tgz; do
  echo "Installing $tarball..."
  npm install "./$tarball" >/dev/null
done

# Now run --manifest and --json for all workers
# The executables are usually npx fde-<worker> or npx @fde-lab/<worker>
for pkg_dir in /Users/sumitg/Projects/fde-lab/packages/*; do
  if [ -d "$pkg_dir" ]; then
    pkg_name=$(basename "$pkg_dir")
    if [ "$pkg_name" != "cli-core" ]; then
      bin_name="fde-${pkg_name}"
      echo "Testing $bin_name --manifest..."
      npx "$bin_name" --manifest > manifest.json
      python3 -m json.tool manifest.json >/dev/null || { echo "FAIL JSON manifest $bin_name"; exit 1; }
      
      echo "Testing $bin_name --json..."
      npx "$bin_name" --json > result.json
      python3 -m json.tool result.json >/dev/null || { echo "FAIL JSON result $bin_name"; exit 1; }
    fi
  fi
done

echo "ALL CLEAN ROOM CHECKS PASSED"
