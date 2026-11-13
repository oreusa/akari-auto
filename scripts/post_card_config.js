// 関東 LIFE NOTE の表紙の絵の設定（post_card.js が読む）。絵は site/card/ に入れて main へ（page.yml の公開で出る）
const path=require('path');const R=path.join(__dirname,'..');
module.exports={logo:path.join(R,'site','logo.png'),brand:'LIFE NOTE',out:path.join(R,'site','card'),base:'https://lifenote-kanto.pages.dev/card/'};
