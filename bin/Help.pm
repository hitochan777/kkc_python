#=====================================================================================
#                       Help.pm
#                             bShinsuke Mori
#                             Last change 9 June 2010
#=====================================================================================

# 機  能 : スクリプトのドキュメントを表示する。
#
# 実  例 : なし
#
# 注意点 : スクリプトにドキュメントが添付されていること。
#          スクリプトに空行が適切に挿入されていること。


#-------------------------------------------------------------------------------------
#                        check arguments
#-------------------------------------------------------------------------------------

sub Help{
    (@_ == 1) || die;

    my($SCRIPT) = shift;
    $/ = "\n\n\n";
    open(SCRIPT, $SCRIPT) || die;
    @line = <SCRIPT>;
    print STDERR $line[0], $line[$#line];
    close(SCRIPT);

    exit(0);
}


#-------------------------------------------------------------------------------------
#                        return
#-------------------------------------------------------------------------------------

1;


#=====================================================================================
#                        END
#=====================================================================================