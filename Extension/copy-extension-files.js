const fs = require('fs');
const path = require('path');

const sourceDir = __dirname;
const buildDir = path.join(__dirname, 'build');

// Files to copy
const filesToCopy = [
  'manifest.json',
  'background.js',
  'popup.html',
  'popup.js',
  'cursor-textbox.js'
];

// Directories to copy
const dirsToCopy = [
  'icons'
];

// Copy files
filesToCopy.forEach(file => {
  const sourcePath = path.join(sourceDir, file);
  const destPath = path.join(buildDir, file);
  
  if (fs.existsSync(sourcePath)) {
    fs.copyFileSync(sourcePath, destPath);
    console.log(`✓ Copied ${file}`);
  } else {
    console.log(`⚠ ${file} not found, skipping`);
  }
});

// Copy directories
dirsToCopy.forEach(dir => {
  const sourcePath = path.join(sourceDir, dir);
  const destPath = path.join(buildDir, dir);
  
  if (fs.existsSync(sourcePath)) {
    // Remove existing directory if it exists
    if (fs.existsSync(destPath)) {
      fs.rmSync(destPath, { recursive: true, force: true });
    }
    // Copy directory
    fs.cpSync(sourcePath, destPath, { recursive: true });
    console.log(`✓ Copied ${dir}/`);
  } else {
    console.log(`⚠ ${dir}/ not found, skipping`);
  }
});

// Copy config.js if it exists (optional, might not be in git)
const configSource = path.join(sourceDir, 'config.js');
const configDest = path.join(buildDir, 'config.js');
if (fs.existsSync(configSource)) {
  fs.copyFileSync(configSource, configDest);
  console.log(`✓ Copied config.js`);
} else {
  console.log(`⚠ config.js not found (this is normal if not configured yet)`);
}

console.log('\n✅ Extension files copied successfully!');

