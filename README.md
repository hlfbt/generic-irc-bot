# generic-irc-bot
Just yet another Generic (modular) IRC Bot.

Currently it is only a simple [ZNC](http://wiki.znc.in/ZNC) python plugin,
because I am too lazy to write my own IRC library for python3 and I cannot find good already existing ones :(


## Usage

Simply add this to your ZNC's module directory and enable the global Python module, then you should be able to enable the GIB module.
The bots modules directory is `gib/`, relative from ZNC's module directory (so for instance `/etc/znc/modules/gib/`).


## Examples

In these examples, the nick of the bot is 'Sawako'.

In a channel:  

    <@sumire> hi Sawako
    <@Sawako> 今日は sumire!
    -Sawako- Possible commands: .help [cmd], .g query, .wa query, .ann query, .anidb query, .mu query, .btt query, .mal query, .vgmdb query, .vndb query, .np [usr], .trans text [.to lng] [.from lgn]
     ...
    <@sumire> .mu one punch man
    <@Sawako> https://www.mangaupdates.com/series.html?id=80345 :: 8 Volumes (Ongoing) :: 9.2 - 1208 votes :: Onepunch-Man
    <@Sawako> In this new action-comedy, everything about a young man named Saitama screams "AVERAGE," from his lifeless expression, to his bald head, to his unimpressive physique. However, this average-looking fellow doesn't have your average problem... He's actually a superhero that's looking for tough opponents! The problem is, every time he finds a promising candidate he beats the snot out of them in one punch. Can Saitama finally find an evil villain stro ...


Via PM:  

    <sumire> reloadmod batoto
    <Sawako> Mod batoto succesfully (re)loaded!


modules.log:

    [2015-02-28 17:31:11] |   INFO: GIB started!
    [2015-05-10 23:01:31] |   INFO: #botspam       call: .mu, args: ['one', 'punch', 'man']
    [2015-05-10 23:01:33] |   INFO: #botspam       finish: .mu, (1534ms)
    [2015-05-10 23:02:50] |   WARN: Module 'batoto' was reloaded.
    [2015-05-10 23:19:46] |  ERROR: Catastrophical error at broken: No module named broken
