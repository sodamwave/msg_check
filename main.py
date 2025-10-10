# main.py

import discord
import os
import re
import threading
from flask import Flask, jsonify, render_template
from datetime import datetime, timezone, timedelta

# -------------------------------------
# 설정
# -------------------------------------
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
TARGET_CHANNEL_ID = int(os.environ.get('TARGET_CHANNEL_ID'))

# ★★★ 생략된 부분 없이 모든 UUID를 포함한 최종 목록 ★★★
UUID_MAP = {
    "B6254D56-1931-8E9A-6F2C-C413BCA4F6CB": "1번 컴퓨터", "00F54D56-3471-F7DA-19A0-25962FD3EDD4": "2번 컴퓨터",
    "698A4D56-6628-2370-1786-F01F6FB8E011": "3번 컴퓨터", "758B4D56-184F-DCCE-BA13-5125C618E676": "4번 컴퓨터",
    "DF1F4D56-5DC5-8F54-464D-64A208A271FA": "5번 컴퓨터", "C6144D56-3194-835A-DBC7-220B047B5C38": "6번 컴퓨터",
    "AD164D56-9697-F145-06F9-234427A81542": "7번 컴퓨터", "EF424D56-FEF3-865F-0813-CF592A20BFB9": "8번 컴퓨터",
    "8F3D4D56-F7B9-2BF2-9759-BC51850C4FB5": "9번 컴퓨터", "38604D56-CA2C-9EAB-EE8C-A5027CA9DF1F": "10번 컴퓨터",
    "38D04D56-D069-560A-C0F2-8134C084F51A": "11번 컴퓨터", "3ECC4D56-5665-E689-A421-6A75E2798EA9": "12번 컴퓨터",
    "F4744D56-1E66-CFDC-E512-A24802575046": "13번 컴퓨터", "DCE74D56-891C-259C-A4EC-87E48E9A39A0": "14번 컴퓨터",
    "069A4D56-ADEE-74CB-7729-25A61926BA69": "15번 컴퓨터", "70324D56-4240-E7D1-F25F-93E487BC78E0": "16번 컴퓨터",
    "21CE4D56-1E0B-D46C-735F-556944AD480E": "17번 컴퓨터", "458A4D56-6DC9-CDE5-2E5B-597D96EA2DF7": "18번 컴퓨터",
    "21BB4D56-AD5E-9987-3C9C-489393604DD7": "19번 컴퓨터", "98C14D56-B179-C5B6-5EA2-2BCC33F9D397": "20번 컴퓨터",
    "FFEA4D56-A459-CAA5-9533-AA1E22B6DA5D": "21번 컴퓨터", "26C94D56-5A33-763F-9A0B-5F4CDDDDC7EC": "22번 컴퓨터",
    "02B74D56-4356-E327-0543-F4167E26BFE4": "23번 컴퓨터", "08194D56-50B6-DF50-65BA-FD3A19552DAE": "24번 컴퓨터",
    "21BB4D56-AD5E-9987-3C9C-489393604DD7": "25번 컴퓨터", "B33F4D56-13AB-B623-446F-77DE3A87796B": "26번 컴퓨터",
    "48C64D56-F985-BA3B-C9C5-7D79DD23B38F": "27번 컴퓨터", "34084D56-BF8D-5C8A-9716-B76B2A599DA5": "28번 컴퓨터",
    "2B0D4D56-EE0A-6D93-F5DE-B5228B34492C": "29번 컴퓨터", "B8A74D56-DAEC-438C-79A7-F679E4BE38CF": "30번 컴퓨터",
    "9C764D56-5C92-E4FB-0876-9FA5F24CFCEB": "31번 컴퓨터", "136D4D56-75C7-3E35-3265-82E06F38590B": "32번 컴퓨터",
    "FB4B4D56-BCAD-A688-3BBB-3852183AF890": "33번 컴퓨터", "8C954D56-F871-9F2C-BD05-06C0C697A1DB": "34번 컴퓨터",
    "D8F84D56-7C5C-DD5A-B83F-FF721A44631D": "35번 컴퓨터", "89084D56-8154-DD3A-7309-730605E29ADE": "36번 컴퓨터",
    "CB814D56-26FA-C719-88A3-5A9352ADDD18": "37번 컴퓨터", "EEE74D56-EC3D-519E-65D5-0542F2943FB7": "38번 컴퓨터",
    "C1624D56-4416-42C0-A00F-921FC1561D91": "39번 컴퓨터", "DCF64D56-B2D6-A192-600D-13663D8FE5F2": "40번 컴퓨터",
    "4B9F4D56-5555-A0F4-1A02-ECB5D4963487": "41번 컴퓨터", "F2CC4D56-3B73-EC7F-CF91-B61E41F68992": "42번 컴퓨터",
    "E0624D56-2283-3A43-B01B-A76432FDE910": "43번 컴퓨터", "57D84D56-5D42-A290-2247-47AAEEC47A0C": "44번 컴퓨터",
    "789C4D56-B1E5-3BA8-E22C-02205EDE71DA": "45번 컴퓨터", "9CA94D56-2742-D902-ACDC-75171972A93E": "46번 컴퓨터",
    "9CA94D56-2742-D902-ACDC-75171972A93E": "47번 컴퓨터", "D5764D56-DCAE-D79A-545B-59F10D394804": "48번 컴퓨터",
    "4E484D56-46DE-ACCF-1100-D8727E891F63": "49번 컴퓨터", "F17F4D56-5570-7579-8555-18129601B8AD": "50번 컴퓨터",
    "11424D56-8BBF-E8F0-6AA0-BA1B6738A31B": "51번 컴퓨터", "67E14D56-4B66-04B7-0946-E80D0BBCAA0A": "52번 컴퓨터",
    "28354D56-1929-2BE0-78DC-02847872655B": "53번 컴퓨터", "F3374D56-4559-B5E8-F0A9-58B43DF65A04": "54번 컴퓨터",
    "14F64D56-34C5-F375-4F34-0EEA9DB51071": "55번 컴퓨터", "DCDA4D56-5A60-964F-F5F9-C513CE621170": "56번 컴퓨터",
    "1C874D56-DFB0-327B-4B4E-D7E5A3320998": "57번 컴퓨터", "0A534D56-FF02-5B08-C218-5D77AD76685E": "58번 컴퓨터",
    "01174D56-49EE-FD2C-38C0-61BC5387D00E": "59번 컴퓨터", "27D14D56-4B3A-3DF1-AAA4-CBEA0930FF8D": "60번 컴퓨터",
    "85934D56-33BA-3B2B-6CFD-5C6ECFC7751D": "61번 컴퓨터", "0F154D56-29E9-933F-7679-0FD48C510530": "62번 컴퓨터",
    "0C184D56-D9B6-BC5A-F6D2-DC05B05DA6BB": "63번 컴퓨터", "D02A4D56-C352-C23C-F598-C2762FE69DD0": "64번 컴퓨터",
    "B31C4D56-3E8F-7DCE-1799-6B01A68B8693": "65번 컴퓨터", "FAEF4D56-25A8-B818-DDE3-CC1C5827652F": "66번 컴퓨터",
    "4DA34D56-5BAA-A3CC-CAE4-B6B126B19AE6": "67번 컴퓨터", "E5EB4D56-9167-FDC0-409D-E2792CF0A29B": "68번 컴퓨터",
    "0DBC4D56-9317-6718-09A3-3A63E34B680F": "69번 컴퓨터", "0F094D56-484E-238E-6A15-4A99D36C75D7": "70번 컴퓨터",
    "912E4D56-7B3C-40F0-6541-2DD718087BC4": "71번 컴퓨터", "F4D54D56-3C16-D7A7-E422-11A9CFB0481A": "72번 컴퓨터",
    "F5C84D56-0DEE-ABDD-4031-2A439FED1EE4": "73번 컴퓨터", "411D4D56-C324-32F5-81F7-19D684372083": "74번 컴퓨터",
    "7D684D56-4630-B174-0C6A-0A5F6EA809E7": "75번 컴퓨터", "5D0C4D56-D01B-6EC6-C249-C2564FA84AF4": "76번 컴퓨터",
    "98C84D56-C7E9-4364-3E7B-5832C15EC7F0": "77번 컴퓨터", "119F4D56-35AE-138F-2F13-1394E7A18908": "78번 컴퓨터",
    "DBED4D56-44E3-9727-1732-C13774844C3E": "79번 컴퓨터", "08164D56-3B84-49A3-1F23-4381CCBCE138": "80번 컴퓨터",
    "5EE74D56-22DA-98AC-951E-38AA6309EEC6": "81번 컴퓨터", "37714D56-A917-116A-7109-5745ADA95BD7": "82번 컴퓨터",
    "CF514D56-65A8-EC7C-0429-FE0F45E5D46B": "83번 컴퓨터", "FC6E4D56-605B-E695-6491-05728F651694": "84번 컴퓨터",
    "948B4D56-FBCB-C0BE-A886-0631719CBF92": "85번 컴퓨터", "85014D56-1060-C870-9C86-C7FC58DE1EF2": "86번 컴퓨터",
    "A7F84D56-558E-A3BE-0E91-8CFBF567C683": "87번 컴퓨터", "83FD4D56-590C-ED0B-3EF9-02AEBD5B6C53": "88번 컴퓨터",
    "CA4A4D56-46C1-C3AD-255C-3CAB38FB26DA": "89번 컴퓨터", "B87D4D56-6800-C635-9ECC-959008CE1E02": "90번 컴퓨터",
    "0CF64D56-9B48-1148-A707-A582FA2198C4": "91번 컴퓨터", "57C44D56-A72A-1784-D3F8-E06F36E8BDD8": "92번 컴퓨터",
    "5A594D56-0766-85D6-D681-537FD9403362": "93번 컴퓨터", "85EC4D56-8FC5-E15C-FB36-299340DFD6C2": "94번 컴퓨터",
    "47E64D56-A18F-58E2-FF3A-2B628388C042": "95번 컴퓨터", "20E54D56-0FF1-7931-20A3-18DA6FA47F62": "96번 컴퓨터",
    "CBBC4D56-3392-3686-C62D-C9FFC2531351": "97번 컴퓨터", "91AF4D56-941F-9F67-C96C-6F81E34DB77F": "98번 컴퓨터",
    "1B154D56-A849-FF1F-259B-E93EC86F026F": "99번 컴퓨터", "23264D56-0B6C-F352-5FC3-D17AE6645A7D": "100번 컴퓨터",
    "D3B84D56-6A43-360E-3E57-3988C5D3ACA1": "101번 컴퓨터", "61314D56-9138-7D59-E5EB-6B34BB5ADAC4": "102번 컴퓨터",
    "8C244D56-6E4B-5745-4EED-E00CBB95275C": "103번 컴퓨터", "FDB34D56-0CA9-ECF3-6252-C7C0E5766EB4": "104번 컴퓨터",
    "37744D56-1ED4-CFBC-BEC6-EC49DE5A5447": "105번 컴퓨터", "2BE94D56-0D93-C8B6-DB6B-1C68ACF4E9B0": "106번 컴퓨터",
    "12D94D56-45B7-344A-9F7B-CE1742B0A160": "107번 컴퓨터", "DFAE4D56-E8F8-7981-6B38-31C5FD03E5CE": "108번 컴퓨터",
    "8B144D56-A5CA-B5D4-DEAB-C31BD1F131AB": "109번 컴퓨터", "4E614D56-48F4-E3F9-3ED8-3C516D587F0B": "110번 컴퓨터",
    "730D4D56-9996-F446-7FC2-C5854DD34D11": "111번 컴퓨터", "557F4D56-07A9-205F-01BB-83A560CF4811": "112번 컴퓨터",
    "82734D56-47C4-A24F-F615-D88B623038FC": "113번 컴퓨터", "01A24D56-8C2D-1664-7E47-0110D0C53697": "114번 컴퓨터",
    "4DDF4D56-447E-F9B0-F826-92827F5D336C": "115번 컴퓨터", "F0A04D56-049A-A488-2742-467BCFD12DF9": "116번 컴퓨터",
    "E2764D56-A60B-9477-BA26-E86837CC727D": "117번 컴퓨터", "D7504D56-CF94-4635-0EC2-61415CAE9C19": "118번 컴퓨터",
    "F8564D56-7806-BE95-EC40-DBB69C4F212C": "119번 컴퓨터", "54D24D56-0A13-638C-FC59-9D3A817A5604": "120번 컴퓨터",
    "DCA24D56-3F04-F663-F576-78E4B357FF2E": "121번 컴퓨터", "4F594D56-1FBF-AD86-6039-0617730E024B": "122번 컴퓨터",
    "DAA14D56-8444-5DFB-970E-80139DB8403E": "123번 컴퓨터", "77494D56-7357-A700-7CE7-5195CC4F5BDD": "124번 컴퓨터",
    "A65D4D56-7407-2640-8A06-4720ED0CB082": "125번 컴퓨터", "50264D56-D27F-029F-E6AD-1B7A192156BD": "126번 컴퓨터",
    "F4D84D56-43E8-6EE2-CBD5-F7B77C9221F1": "127번 컴퓨터", "FA9E4D56-3FA6-AF19-F786-5923C38940C7": "128번 컴퓨터",
    "8DBB4D56-EEE5-8E9E-4F6B-5FA4DCD4BF32": "129번 컴퓨터", "52DA4D56-2709-7027-1563-D80961D98AED": "130번 컴퓨터",
    "0B5F4D56-689F-C021-A6E2-90B6D4E616B2": "131번 컴퓨터", "46FF4D56-98E3-429B-159B-259A880E4C38": "132번 컴퓨터",
    "0DC44D56-94CF-86DD-5F46-D9A52C32B5C0": "133번 컴퓨터", "8C494D56-5F01-C75F-045D-256ABDC3F8B5": "134번 컴퓨터",
    "22D84D56-AE24-5D0D-9BCD-2559D315107E": "135번 컴퓨터", "90434D56-0815-C01A-A376-A51BA157DBD1": "136번 컴퓨터",
    "13A64D56-F535-450B-8720-BA283EBCCC34": "137번 컴퓨터", "82274D56-5D26-8952-3DE8-F63BD44B39C1": "138번 컴퓨터",
    "6E6C4D56-A7DF-F985-28FC-EDAD429B9E8F": "139번 컴퓨터", "0AAA4D56-0F9B-159D-E414-688065AB11F6": "140번 컴퓨터",
    "7FA34D56-9263-30F6-1C7E-5198E7E86F4E": "141번 컴퓨터", "B67F4D56-D6F0-9840-FC50-310659CD0A4B": "142번 컴퓨터",
    "536A4D56-A40E-1AC9-638F-C3FD34FB2780": "143번 컴퓨터", "D5E44D56-43D1-1BB8-B612-F6660660410B": "144번 컴퓨터",
    "5DE74D56-F466-74C2-654E-0157AD28242E": "145번 컴퓨터", "13514D56-ADC0-8A01-0403-02FF2CD34390": "146번 컴퓨터",
    "EE5A4D56-C18C-EE35-3CD9-B0317BAAE32B": "147번 컴퓨터", "F7C94D56-229D-B91B-CA5A-D26682D2E8F4": "148번 컴퓨터",
    "9DEB4D56-CF4C-0562-62B9-28DAD50C1ED5": "149번 컴퓨터", "FC8F4D56-DBC8-9879-80C2-58BFD8E8D620": "150번 컴퓨터",
    "4DEB4D56-F2AB-001E-5CB1-EB00EF30AE65": "151번 컴퓨터", "F5A84D56-D091-19D7-A82A-9CCF8838869A": "152번 컴퓨터",
    "F7BB4D56-54B0-8B09-60D2-10EFF5C8C70B": "153번 컴퓨터", "70844D56-F7B9-F7D1-3161-2867F5D4A1FA": "154번 컴퓨터",
    "24274D56-7142-64F3-539C-08089530E280": "155번 컴퓨터", "4CF64D56-2617-8A51-BD08-34250D223112": "156번 컴퓨터",
    "28934D56-CEBC-13FC-1BF0-DAD8EB2F79F3": "157번 컴퓨터", "1E024D56-1218-E8CD-5445-D82DB32A3779": "158번 컴퓨터",
    "F10F4D56-1D0E-EA23-412A-2A4451923552": "159번 컴퓨터", "2D184D56-5DBC-B7D6-7E8F-98D481AC8186": "160번 컴퓨터",
    "7B704D56-6BD7-B48C-368B-653AF180A82B": "161번 컴퓨터", "4F104D56-0C12-153D-1443-040330F878D9": "162번 컴퓨터",
    "447F4D56-C432-AAE1-AF47-74639644261B": "163번 컴퓨터", "111F4D56-5243-42F2-F590-90D2DA6A796A": "164번 컴퓨터",
    "53B14D56-48CD-B35C-BB83-034FA685A483": "165번 컴퓨터", "0C794D56-6419-8C05-8F87-0AAC82C9814C": "166번 컴퓨터",
    "EF0D4D56-1569-234D-1859-A173D29B29E3": "167번 컴퓨터", "87E94D56-2C05-6FD2-5E55-E8B8B923E9AD": "168번 컴퓨터",
    "82BB4D56-40E8-4023-43DB-53C4B7B7EC1C": "181번 컴퓨터", "0AB84D56-8CDC-A215-E9E1-1BFCF11C55C9": "182번 컴퓨터",
    "74D54D56-E7BF-019E-161A-3DD403BF3E00": "183번 컴퓨터", "E5D74D56-0B34-75C4-3D71-A42DF9317DA4": "184번 컴퓨터",
    "15584D56-4824-AE41-64F3-42BC5DE9AE97": "185번 컴퓨터", "3C4A4D56-D110-8D0D-3477-D05E075B0006": "186번 컴퓨터",
    "D2CB4D56-5C01-E05C-60B2-508D17B6052C": "187번 컴퓨터", "8EC24D56-4576-9A61-6CD0-1E10DC9313E5": "188번 컴퓨터",
    "78BF4D56-03DB-782E-9C9E-291F78094CB7": "189번 컴퓨터", "BE8E4D56-6A64-ED18-5246-D8F58E3D2DB7": "190번 컴퓨터",
    "6AD34D56-B5BE-AE6F-C257-0890C8502B3C": "191번 컴퓨터", "34EC4D56-9C18-EDF5-2FDB-76A9F76CE70A": "192번 컴퓨터",
    "4FDB4D56-3628-B8F5-C6B1-A04043C27381": "193번 컴퓨터", "A0944D56-AC16-2BA1-06E8-E0DDCF160748": "194번 컴퓨터",
    "B9A04D56-B062-12AE-6DEA-54638A3A618C": "195번 컴퓨터", "A9504D56-0E97-CF35-29B7-84EF9A48483B": "196번 컴퓨터",
    "09484D56-0250-F63F-F371-C792B084509B": "197번 컴퓨터", "D68F4D56-E5FA-71BF-A3D0-B030A6A99E4E": "198번 컴퓨터",
    "0A0E4D56-855D-108F-BD73-0CF7E138A028": "199번 컴퓨터", "9AE74D56-0F0B-8A72-5BA6-DFAD7F7256EB": "200번 컴퓨터",
    "43B14D56-CAC6-F0C7-B2B3-D786718F10E1": "201번 컴퓨터", "5E1C4D56-10D1-248E-96BD-D3911E0C5270": "202번 컴퓨터",
    "70F74D56-D493-C7A5-1A0D-5419CB4BDB57": "203번 컴퓨터", "88404D56-C6DA-56A5-687E-94D90ED059EC": "204번 컴퓨터",
    "B07A4D56-E9C0-BDC4-571D-03C75300FFC5": "205번 컴퓨터", "5D8A4D56-7005-BEA5-5AF9-D21946AF0129": "206번 컴퓨터",
    "01304D56-97EF-877C-42FC-165F49489011": "207번 컴퓨터", "18BF4D56-ED3F-0CF7-7526-07D92A5D3598": "208번 컴퓨터",
    "65C04D56-F6CE-1C53-D65D-53D7BDA38A83": "209번 컴퓨터", "53E04D56-6882-E72F-1C86-71960E530B50": "210번 컴퓨터",
    "FFA74D56-E423-A4D8-2D22-131772B484D3": "211번 컴퓨터", "E1804D56-D252-8F58-9029-AA464C946387": "212번 컴퓨터",
    "242C4D56-18C0-D810-EA9F-028D8E067478": "213번 컴퓨터", "E5EF4D56-DF55-C87F-3F7E-4C75A34DBDDC": "214번 컴퓨터",
    "90F94D56-28DF-0947-BD2C-2A0A2917AF57": "215번 컴퓨터", "267A4D56-BB8C-D558-413D-D8C2CBD6A132": "216번 컴퓨터",
    "25AC4D56-DBD5-7697-7641-32B3DB743001": "217번 컴퓨터", "52924D56-A7DA-B71F-C9E9-87469B896512": "218번 컴퓨터",
    "32784D56-D25E-B3BE-89B1-BBA0835606D6": "219번 컴퓨터", "114F4D56-5EED-5C06-D988-F257587178A3": "220번 컴퓨터",
    "7BB04D56-ACD0-241B-C395-09185C8F9B6D": "221번 컴퓨터", "722A4D56-C3BE-9938-3C64-6BFE43D1A540": "222번 컴퓨터",
    "468A4D56-B9B5-DDE1-8CB2-AC35CE57AC04": "223번 컴퓨터", "D59A4D56-847E-7F9A-D8A9-899C59140A02": "224번 컴퓨터",
    "73954D56-EA85-F704-E1D9-8F6E1CA04CE2": "225번 컴퓨터", "AEC64D56-90ED-7D97-D10C-16A9FB897CDA": "226번 컴퓨터",
    "66B84D56-6F31-C15D-1EC5-6C45BD58B53C": "227번 컴퓨터", "33044D56-4BAE-F340-46FA-16642EF8A1EB": "228번 컴퓨터",
    "8DC74D56-BE45-D65C-D4BC-F76E1E021688": "229번 컴퓨터", "B2404D56-082C-B290-53D5-BE5ADE383A8A": "230번 컴퓨터",
    "2D6B4D56-FC68-6195-DE9C-6AD2B629B59E": "231번 컴퓨터", "88A34D56-E812-9F18-BA46-8F59CE4CF59C": "232번 컴퓨터",
    "34244D56-96BB-55F6-CEA1-D75FACC7E729": "233번 컴퓨터", "AB344D56-9A1F-005A-2DCD-A9CFD5DEE67B": "234번 컴퓨터",
    "82914D56-5F10-8554-F102-39207EDC8D76": "235번 컴퓨터", "66CC4D56-9DD0-E3A8-1BB8-12421D74432F": "236번 컴퓨터",
    "E4604D56-D076-4C8E-A1AE-C6C4F142F2A6": "237번 컴퓨터", "F8EC4D56-1054-E789-AAAA-017B06A91F05": "238번 컴퓨터",
    "6F544D56-2B92-1F01-86F4-AC02B3A075E5": "239번 컴퓨터", "D5A84D56-8B53-1026-891A-454A64FA10CD": "240번 컴퓨터"
}


computer_statuses = {}
status_lock = threading.Lock()
app = Flask(__name__)

def initialize_statuses():
    TOTAL_COMPUTERS = 240
    registered_names = set(UUID_MAP.values())
    kst = timezone(timedelta(hours=9))
    now_iso = datetime.now(kst).isoformat()

    for i in range(1, TOTAL_COMPUTERS + 1):
        computer_name = f"{i}번 컴퓨터"
        
        # ### 수정 시작 ### : fileName 필드 추가
        initial_data = {
            'log_timestamp': '-',
            'last_update': now_iso,
            'fileName': '-'  # 파일 이름 필드 초기화
        }
        # ### 수정 끝 ###

        if computer_name in registered_names:
            if computer_name not in computer_statuses:
                computer_statuses[computer_name] = {
                    'status': '최근 로그 없음',
                    **initial_data
                }
        else:
            computer_statuses[computer_name] = {
                'status': 'UUID 없음',
                **initial_data
            }
            
    if "" in UUID_MAP:
        computer_statuses["UUID 없음"] = {
            'status': '최근 로그 없음',
            **initial_data
        }

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

UUID_PATTERN = re.compile(r'([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12})', re.IGNORECASE)
LOG_TIMESTAMP_PATTERN = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]')

def parse_and_update_status(message_content):
    uuid_match = UUID_PATTERN.search(message_content)
    uuid = uuid_match.group(1).upper() if uuid_match else ""
    display_name = UUID_MAP.get(uuid, uuid) if uuid else UUID_MAP.get("")

    status = None
    timestamp_match = LOG_TIMESTAMP_PATTERN.search(message_content)
    log_timestamp = timestamp_match.group(1) if timestamp_match else "N/A"

    if "__시작" in message_content: status = "시작"
    elif "__종료" in message_content: status = "종료"

    # ### 수정 시작 ### : 파일 이름 추출 로직 추가
    file_name = "-"
    if uuid_match:
        # UUID 앞부분의 문자열을 가져옴
        pre_uuid_str = message_content.split(uuid)[0]
        # 타임스탬프 '] ' 뒷부분을 가져옴
        if ']' in pre_uuid_str:
            raw_name_part = pre_uuid_str.split(']', 1)[1].strip()
            # '_V' 로 시작하는 버전 정보를 제거
            file_name = re.split(r'_V\d', raw_name_part)[0].strip('_')
    # ### 수정 끝 ###
    
    if status and display_name:
        kst = timezone(timedelta(hours=9))
        server_check_time = datetime.now(kst).isoformat()
        with status_lock:
            # ### 수정 시작 ### : computer_statuses에 fileName 추가
            computer_statuses[display_name] = {
                'status': status,
                'log_timestamp': log_timestamp,
                'last_update': server_check_time,
                'fileName': file_name 
            }
            # ### 수정 끝 ###
        print(f"[상태 업데이트] {display_name}, 상태: {status}, 파일: {file_name}, 로그일시: {log_timestamp}")

@client.event
async def on_ready():
    print(f'{client.user} (으)로 로그인했습니다.')
    initialize_statuses()
    channel = client.get_channel(TARGET_CHANNEL_ID)
    if channel:
        print(f"'{channel.name}' 채널의 최근 1000개 메시지를 스캔합니다.")
        messages = [message async for message in channel.history(limit=1000)]
        for message in reversed(messages):
            parse_and_update_status(message.content)
        print("초기 상태 설정 완료.")

@client.event
async def on_message(message):
    if message.author == client.user: return
    if message.channel.id == TARGET_CHANNEL_ID:
        parse_and_update_status(message.content)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/status')
def get_statuses():
    with status_lock:
        return jsonify(computer_statuses)

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    if not DISCORD_TOKEN or not TARGET_CHANNEL_ID:
        print("오류: DISCORD_TOKEN 또는 TARGET_CHANNEL_ID 환경 변수가 설정되지 않았습니다.")
    else:
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()
        client.run(DISCORD_TOKEN)
