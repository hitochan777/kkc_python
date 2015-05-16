#!/usr/bin/perl
#=====================================================================================
#                       kkc-word-1.perl
#                           by Shinsuke Mori
#                           Last change : 9 June 2010
#=====================================================================================

# 機  能 : 統計的手法による仮名漢字変換 (単語と入力記号列の組の1-gramモデル)
#
# 使用法 : kkc-word-1.perl (TRAINING CORPUS)
#
# 実  例 : kkc-word-1.perl ../corpus/L.wordkkci < ../corpus/T.kkci
#
# 注意点 : 変換する入力記号列は標準入力に与える
#          そのほかいっぱいある
#
# 参  考 : http://plata.ar.media.kyoto-u.ac.jp/mori/research/


#-------------------------------------------------------------------------------------
#                        require
#-------------------------------------------------------------------------------------

use Env;
use File::Basename;
unshift(@INC, dirname($0));

require "Help.pm";


#-------------------------------------------------------------------------------------
#                        check arguments
#-------------------------------------------------------------------------------------

((@ARGV == 1) && ($ARGV[0] ne "-help")) || &Help($0);

$LC = shift;


#-------------------------------------------------------------------------------------
#                        set variables
#-------------------------------------------------------------------------------------

($BT, $UT) = ("BT", "UT");                        # 文末記号, 未知語記号

$UTMAXLEN = 4;                                    # 未知語の最大長
@KKCInput = &KKCInput;                            # 入力記号集合
$CharLogP = log(1+scalar(@KKCInput));             # 入力記号0-gram確率の負対数値


#-------------------------------------------------------------------------------------
#                        言語モデル %PairFreq の生成
#-------------------------------------------------------------------------------------

%PairFreq = ();                                   # 単語/入力記号列 => 頻度

open(LC) || die "Can't open $LC: $!\n";           # 学習コーパス
print STDERR "Reading $LC ... ";
while (<LC>){
    map($PairFreq{$_}++, split);                  # 各組の頻度をインクリメント
    $PairFreq{$BT}++;                             # 文末記号の頻度をインクリメント
}
warn "done\n";
close(LC);

#printf(STDERR "%4d %s\n", $PairFreq{$_}, $_) foreach keys(%PairFreq);


#-------------------------------------------------------------------------------------
#                        スムージング
#-------------------------------------------------------------------------------------

$Freq = 0;                                        # f() = Σf(word/kkci)
@pair = keys(%PairFreq);
foreach $pair (@pair){
    $freq = $PairFreq{$pair};
#    printf(STDERR "%4d %s\n", $pair, $freq);
    $Freq += $freq;
    if ($freq == 1){                              # 頻度が１の場合
        $PairFreq{$UT} += $freq;                  # f(UT) に加算して
        delete($PairFreq{$pair});                 # f(pair) を消去
    }
}


#-------------------------------------------------------------------------------------
#                        仮名漢字変換辞書 %Dict の作成
#-------------------------------------------------------------------------------------

%Dict = ();                                       # KKCI => <Word, KKCI>+
foreach $pair (keys(%PairFreq)){                  # f(∀pair) > 0 に対するループ
    (($pair eq $BT) || ($pair eq $UT)) && next;   # 特殊記号は辞書にいれない
    $kkci = (split("/", $pair))[1];               # 入力記号列部分
    defined($Dict{$kkci}) || ($Dict{$kkci} = []); # 必要なら $Dict{$kkci} の初期化
    push(@{$Dict{$kkci}}, $pair);                 # dict(KKCI) に追加
}

#printf("%s => %s\n", $_, join(", ", @{$Dict{$_}})) foreach (keys(%Dict));


#-------------------------------------------------------------------------------------
#                        main
#-------------------------------------------------------------------------------------

# 以下入力記号が 2[byte] からなることを仮定
# 仮名漢字変換の本体

while (chop($sent = <>)){                         # テストコーパスのループ
#    print $sent, "\n";
    @result = &KKConv($sent);                     # 変換エンジンを呼ぶ
    print join(" ", @result), "\n";               # 変換結果の表示
#    print join("", map((split("/"))[0], @result)), "\n";
}


#-------------------------------------------------------------------------------------
#                        close
#-------------------------------------------------------------------------------------

exit(0);


#-------------------------------------------------------------------------------------
#                        入力記号集合
#-------------------------------------------------------------------------------------

sub KKCInput{
    (@_ == 0) || die;
    my(@LATINU)   = qw(    Ａ Ｂ Ｃ Ｄ Ｅ Ｆ Ｇ Ｈ Ｉ Ｊ Ｋ Ｌ Ｍ Ｎ Ｏ
                        Ｐ Ｑ Ｒ Ｓ Ｔ Ｕ Ｖ Ｗ Ｘ Ｙ Ｚ );

    my(@NUMBER)   = qw( ０ １ ２ ３ ４ ５ ６ ７ ８ ９ );

    my(@HIRAGANA) = qw(    ぁ あ ぃ い ぅ う ぇ え ぉ お か が き ぎ く 
                        ぐ け げ こ ご さ ざ し じ す ず せ ぜ そ ぞ た
                        だ ち ぢ っ つ づ て で と ど な に ぬ ね の は
                        ば ぱ ひ び ぴ ふ ぶ ぷ へ べ ぺ ほ ぼ ぽ ま み
                        む め も ゃ や ゅ ゆ ょ よ ら り る れ ろ ゎ わ
                        ゐ ゑ を ん );

    my(@OTHERS)   = ( qw( ヴ ヵ ヶ ),             # 片仮名のみの文字
                      qw( ー ＝ ¥ ｀ 「 」 ； ’ 、 。 ), # ／ => ・ (if US101)
                      qw( ！ ＠ ＃ ＄ ％ ＾ ＆ ＊ （ ） ＿ ＋ ｜ 〜 ｛ ｝ ： ” ＜ ＞ ？ ),
                      qw( ・ ));                           # for JP106 keyboard

    return(@LATINU, @NUMBER, @HIRAGANA, @OTHERS);
}


#-------------------------------------------------------------------------------------
#                       KKConv
#-------------------------------------------------------------------------------------

# 機  能 : 仮名漢字変換
#
# 注意点 : NODE = <PREV, $pair, $logP>;
#          パラメータはグローバル変数として与えられる

sub KKConv{
    (@_ == 1) || die;
    my($sent) = shift;
    my($POSI) = length($sent)/2;                      # 解析位置 $posi の最大値

    my(@VTable) = map([], (0 .. ($POSI+1)));          # Viterbi Table
    @{$VTable[0]} = (["NULL", $BT, 0]);               # DP左端

    for ($posi = 1; $posi <= $POSI; $posi++){         # 解析位置(辞書引き右端)
        for ($from = 0; $from < $posi; $from++){      # 開始位置(辞書引き左端)
            my($kkci) = substr($sent, 2*$from, 2*($posi-$from));
            foreach $pair (@{$Dict{$kkci}}){          # 既知語のループ
#                printf(STDERR "%s%s(%d)\n", " " x (2*$from), $pair, $PairFreq{$pair});
                my(@best) = ("NULL", "NULL", 0);          # 最良のノード(の初期値)
                foreach $node (@{$VTable[$from]}){
                    my($logP) = ${$node}[2]-log($PairFreq{$pair}/$Freq);
                    if (($best[1] eq "NULL") || ($logP < $best[2])){
                        @best = ($node, $pair, $logP);
#                        printf(STDERR "%s -> %s (%5.2f)\n", ${$node}[1], $pair, $logP);
                    }
                }
                if ($best[1] ne "NULL"){              # 最良のノードがある場合
                    push(@{$VTable[$posi]}, [@best]); # @best をコピーして参照を記憶
                }
            }
            if (($posi-$from) <= $UTMAXLEN){          # 未知語によるノード生成
                my(@best) = ("NULL", "NULL", 0);      # 最良のノード(の初期値)
                foreach $node (@{$VTable[$from]}){
                    my($logP) = ${$node}[2]-log($PairFreq{$UT}/$Freq)
                        +($posi-$from+1)*$CharLogP;   # 入力記号と単語末の BT の生成
                    if (($best[1] eq "NULL") || ($logP < $best[2])){
                        $pair = join("/", $kkci, $UT);
                        @best = ($node, $pair, $logP);
#                        printf(STDERR "%s -> %s (%5.2f)\n", ${$node}[1], $pair, $logP);
                    }
                }
                if ($best[1] ne "NULL"){              # 最良のノードがある場合
                    push(@{$VTable[$posi]}, [@best]); # @best をコピーして参照を記憶
                }
            }
        }
    }

    my(@best) = ("NULL", "NULL", 0);                      # 最良のノード(の初期値)
    #print STDERR scalar(@{$VTable[$posi-1]}), "\n";
    foreach $node (@{$VTable[$posi-1]}){              # $BT への遷移
        $logP = ${$node}[2]-log($PairFreq{$BT}/$Freq);
        if (($best[1] eq "NULL") || ($logP < $best[2])){
            @best = ($node, $BT, $logP);
#            printf(STDERR "%s -> %s (%5.2f)\n", ${$node}[1], $BT, $logP);
        }
    }
    
# 逆向きの探索と変換結果の表示
    my(@result) = ();                                 # 結果 <word, kkci>+
    my($node) = $best[0];                             # 右端のノード
    while (${$node}[0] ne "NULL"){                    # ノードを左向きにたどる
#        print STDERR ${$node}[1], "\n";
        unshift(@result, ${$node}[1]);                # $pair を配列に記憶していく
        $node = ${$node}[0];
    }

    return(@result);
}


#=====================================================================================
#                        END
#=====================================================================================
