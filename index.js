import { diffWords, diffLines } from 'diff';
import fs from 'fs';

const oldText = fs.readFileSync('text1.txt', 'utf-8');
const newText = fs.readFileSync('text2.txt', 'utf-8');

const diff = diffLines(oldText, newText);

let oldLine = 1;
let newLine = 1;

diff.forEach(part => {
  const lines = part.value.split(/\r?\n/).length - 1;
  
  if (part.removed) {
    console.log(`- 削除: 旧ファイル ${oldLine}行目から ${lines}行 (${oldLine}-${oldLine + lines - 1})`);
    console.log(part.value.substring(0, 100) + '...');
    oldLine += lines;
  } else if (part.added) {
    console.log(`+ 追加: 新ファイル ${newLine}行目から ${lines}行 (${newLine}-${newLine + lines - 1})`);
    console.log(part.value.substring(0, 100) + '...');
    newLine += lines;
  } else {
    // 変更なし
    oldLine += lines;
    newLine += lines;
  }
});

console.log('\n--- 元の出力 ---');
console.log(diff);

// asuky@asuky-main:~/poc-textman$ diff text1.txt text2.txt
// 5,8d4
// < Duis aute irure dolor in reprehenderit in voluptate velit.
// < Esse cillum dolore eu fugiat nulla pariatur excepteur sint.
// < Occaecat cupidatat non proident, sunt in culpa qui officia.
// <
// 12a9,12
// > Duis aute irure dolor in reprehenderit in voluptate velit.
// > Esse cillum dolore eu fugiat nulla pariatur excepteur sint.
// > Occaecat cupidatat non proident, sunt in culpa qui officia.
// >
// 25,28d24
// < Facilisis leo vel fringilla est ullamcorper eget nulla.
// < Dignissim diam quis enim lobortis scelerisque fermentum dui.
// < Faucibus interdum posuere lorem ipsum dolor sit amet consectetur.
// <
// 31a28,31
// >
// > Facilisis leo vel fringilla est ullamcorper eget nulla.
// > Dignissim diam quis enim lobortis scelerisque fermentum dui.
// > Faucibus interdum posuere lorem ipsum dolor sit amet consectetur.
// asuky@asuky-main:~/poc-textman$ npm start

// > poc-textman@1.0.0 start
// > node index.js

// (node:2660) [MODULE_TYPELESS_PACKAGE_JSON] Warning: Module type of file:///home/asuky/poc-textman/index.js is not specified and it doesn't parse as CommonJS.
// Reparsing as ES module because module syntax was detected. This incurs a performance overhead.
// To eliminate this warning, add "type": "module" to /home/asuky/poc-textman/package.json.
// (Use `node --trace-warnings ...` to show where the warning was created)
// [
//   {
//     count: 4,
//     added: false,
//     removed: false,
//     value: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.\r\n' +
//       'Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\r\n' +
//       'Ut enim ad minim veniam, quis nostrud exercitation ullamco.\r\n' +
//       '\r\n'
//   },
//   {
//     count: 4,
//     added: false,
//     removed: true,
//     value: 'Duis aute irure dolor in reprehenderit in voluptate velit.\r\n' +
//       'Esse cillum dolore eu fugiat nulla pariatur excepteur sint.\r\n' +
//       'Occaecat cupidatat non proident, sunt in culpa qui officia.\r\n' +
//       '\r\n'
//   },
//   {
//     count: 4,
//     added: false,
//     removed: false,
//     value: 'Deserunt mollit anim id est laborum consectetur adipiscing.\r\n' +
//       'Pellentesque habitant morbi tristique senectus et netus.\r\n' +
//       'Malesuada fames ac turpis egestas sed tempus urna et.\r\n' +
//       '\r\n'
//   },
//   {
//     count: 4,
//     added: true,
//     removed: false,
//     value: 'Duis aute irure dolor in reprehenderit in voluptate velit.\r\n' +
//       'Esse cillum dolore eu fugiat nulla pariatur excepteur sint.\r\n' +
//       'Occaecat cupidatat non proident, sunt in culpa qui officia.\r\n' +
//       '\r\n'
//   },
//   {
//     count: 12,
//     added: false,
//     removed: false,
//     value: 'Pharetra magna ac placerat vestibulum lectus mauris ultrices.\r\n' +
//       'Eros donec ac odio tempor orci dapibus ultrices in.\r\n' +
//       'Iaculis eu non diam phasellus vestibulum lorem sed risus.\r\n' +
//       '\r\n' +
//       'Ultricies mi eget mauris pharetra et ultrices neque ornare.\r\n' +
//       'Aenean sed adipiscing diam donec adipiscing tristique risus.\r\n' +
//       'Nec feugiat nisl pretium fusce id velit ut tortor pretium.\r\n' +
//       '\r\n' +
//       'Viverra ipsum nunc aliquet bibendum enim facilisis gravida.\r\n' +
//       'Neque sodales ut etiam sit amet nisl purus in mollis.\r\n' +
//       'Nunc sed id semper risus in hendrerit gravida rutrum.\r\n' +
//       '\r\n'
//   },
//   {
//     count: 4,
//     added: false,
//     removed: true,
//     value: 'Facilisis leo vel fringilla est ullamcorper eget nulla.\r\n' +
//       'Dignissim diam quis enim lobortis scelerisque fermentum dui.\r\n' +
//       'Faucibus interdum posuere lorem ipsum dolor sit amet consectetur.\r\n' +
//       '\r\n'
//   },
//   {
//     count: 4,
//     added: false,
//     removed: false,
//     value: 'Adipiscing elit pellentesque habitant morbi tristique senectus.\r\n' +
//       'Et netus et malesuada fames ac turpis egestas integer.\r\n' +
//       'Eget magna fermentum iaculis eu non diam phasellus vestibulum.\r\n' +
//       '\r\n'
//   },
//   {
//     count: 4,
//     added: true,
//     removed: false,
//     value: 'Facilisis leo vel fringilla est ullamcorper eget nulla.\r\n' +
//       'Dignissim diam quis enim lobortis scelerisque fermentum dui.\r\n' +
//       'Faucibus interdum posuere lorem ipsum dolor sit amet consectetur.\r\n' +
//       '\r\n'
//   },
//   {
//     count: 7,
//     added: false,
//     removed: false,
//     value: 'Morbi tempus iaculis urna id volutpat lacus laoreet non.\r\n' +
//       'Curabitur gravida arcu ac tortor dignissim convallis aenean.\r\n' +
//       'Et magnis dis parturient montes nascetur ridiculus mus mauris.\r\n' +
//       '\r\n' +
//       'Vitae sapien pellentesque habitant morbi tristique senectus.\r\n' +
//       'Et netus et malesuada fames ac turpis egestas maecenas.\r\n' +
//       'Pharetra sit amet aliquam id diam maecenas ultricies mi eget.'
//   }
// ]