// 関東 TOWN NOTE の表紙の絵の設定（post_card.js・post_glass.js が読む）。絵は site/card/ に入れて main へ（page.yml の公開で出る）
// 11/23 オーナー「関東と関西どっちも完璧に」：名前を関西（KANSAI TOWN NOTE）とそろえ、21時台の枠は関西と同じ夜の形に。
const path=require('path');const R=path.join(__dirname,'..');
module.exports={name:'KANTO TOWN NOTE',night:/-(21\d\d|n7|x21)$/,logo:path.join(R,'site','logo.png'),brand:'TOWN NOTE',out:path.join(R,'site','card'),base:'https://kanto.townnote.app/card/'};
