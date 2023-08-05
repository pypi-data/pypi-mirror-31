
> offline-reader: cmd flag to show all

> check which type of jobid is natively stored in jobtree, string or int?
  Then correct library-wide accordingly.

### 160612: Maintenance
> git commit
> Rename submodule to lowercase
> fix py.test
> setup.py
> tox
> expand coverage


### 160528: Try using Ganga 6.1.20
- This seems to be a stable version.
- I need to migrate to new one now since Dirac call start to be incompat.
- Start up works.
- Missing library problem.
  - This only happens for Ganga on lphe. When I compare the difference on 
    `PYTHONPATH`, this is significant, such that most functions in Ganga simply
    fail miserably. The simple cure is to patch `PYTHONPATH` to mimic the full
    paths, compared from lxplus.
- How to load GangaCK at startup time?
  - Move to use `~/.ganga.py` instead.
  - Hmm, not good enough, it's too early before ipython shell is ready to bind
    the magics... see below
- Import error, `No module named iplib`
  - This is needed for the magic
  - Due to change in ipython version: 0.6.13 --> 1.2.1
  - This is now getting tricky, since the init lifecycle for startup files 
    changes. So far it seems that `~/.ganga.py` is too restricted, 
    and `ipythonrc` is NOT being loaded in 1.2.1...
  - https://ipython.org/ipython-doc/1/
  - Shit,... with v601r20, running `ipython` does load the profile, but `ganga`
    does not load it.
  - 160531: Judging from the new doc and presentation, it seems that `ipythonrc`
    is no longer in used. Only `.ganga.py`. At this point, I have to drop the 
    compat for magics at start-up. I should send email to ask about magic again.
- Is SLURM still compatible with this version?
  - Preliminary, I had a problem. It was probably non-clean environment.
  - Tried again today, with super clean env, it works!
- Write alias to prepare env.
  - I need this since several things are needed now:
    - Changing LbLogin version
    - Correction on PYTHONPATH
  - Let's stick with `SetupGanga`, not `lb-run Ganga` for now.
- Try appending my local config last
  - Motivation: I can then having my setting appended independent of the gangarc
    file at home. Series of appending settings should be possible.
  - Try `GANGA_CONFIG_PATH`
    - No, this one has fixed prefix to installation path.
    - Oh yes, it can. Don't use ~. Starts with absolute prefix /. Nice!
  - Thus, I don't need to worry about `~/.gangarc` anymore.
  - Also, recover the rest of my local config
- Slowly migrate jobs repo back. Slowly. Pickup depreciation along the way.
  - This is because I had a corrupt problem midway yesterday. 
  - Note: Don't do full curation. Just do only those hinder `jobs` command
    as well as the annoying warning. 
  - List of classes to be patched
    - PhysicalFile --> LocalFile
    - SandboxFile  --> LocalFile
    - LogicalFile  --> DiracFile
  - Q: How will Ganga behave if subjobs dirs are archived?
    - There are several benefits:
      - Number of files tracking is drastically reduce. git will be happy.
      - Much less work to be done during this migration too.
      - Hopefully faster start up time too.
    - Try with 4xxx/4022
    - Interesting. It works fine. The mother job can be read, no warning.
    - Will it complain if there's foreign file inside repo? --> No, good.
    - Then, it's so tempting to collapse the subjobs dirs at this point.
      - Let's borrow a snippet from xmlmerge
      - Changes: 225115 files (2GB) --> 1388 files (110Mb)! 2 magnitude!!
      - In a long run, this snippet is probably be integrated into ganga_cleaner
        I'll leave that to the future.
  - Q: How should I approach patching: Manual for Script?
    - Note: It's even more massive when subjobs is taken into account...
    - Writing proper xml parser, patching on dry-run would be the safest way.
    - Due to the collapse of subjobs dirs above, there's less worry about the
      nested structure and much lower number of files to work with. 
  - PhysicalFile
    - Ran a script. Nice. Only `name` is used. 
  - SandboxFile
    - Good, also found that the only attr used is `name` too. 
  - LogicalFile
    - Also good, no complication on attributes
  - Use cElementTree to patch xml files. This is easier than I expected!
  - Finally, slowly migrate it to lphe.
    - Note: Upon first usage, ganga will be building index file. I'm not sure
      which format is it, just give it some time.
  - Migrate jobtree back. I hope it's still intact.
  - Bring back workspace
  - Merge selectively with the latest job on 013contamination.
    - 4677--4695
    - archive + patch locally first, then import into gangadir
    - Opps, some warning, rollback, do it slowly again.
        WARNING  Configuration of EDG for LCG:
        WARNING  File not found: /afs/cern.ch/sw/ganga/install/config/grid_env_auto.sh
    - Most of these jobs are remnant of corrupt jobs during migration.
      Safe to be deleted.
  - Make sure I have the 6.0.44 backup to fallback in case of emergency.
    - Use the one on OSX to make a backup tar, but try not to delete things,
      let git do the work.
  - Finally, apply changes to current git.
    - Move the .git dir to new gangadir
    - Done. Much lighter, much faster!


### ? Migrate to 6.1.20, part II
- Note: It's now compat with Bender+SLURM subjobs. Phew!
  - Note: But this time, bender needs setData inside configure again. Fine.
- Make Magic compat with new iPython, regardless the startup mechanism
  - Use the `@register_line_magic` decorator protocol.
  - Note: Don't call `from IPython import get_ipython`.
    It's already there on the `__main__` namespace.
  - Correct the function signature.
> Idea: If magic at startup doesn't work, how about append it into history
  as last command, such that pressing arrow-up does the trick.
  - where is the history file?
> Compat with LHCbDataset
  > WARNING  PFN is slightly ambiguous, constructing LocalFile
    > Dont use PFN precursor, wrap to LocalFile
> Log duplication problem
  - Let's use PythonCK log only if it's existed.


> 160601: Magic works again in 6.1.20, but the speed is terrible, check me.

> 160503: xmlmerge: show disk size upon requesting archive

> 160420: LHCbDataset.new: Warning upon receiving null list. Probably user's fault.

- 160323 Fix jt orphan column header

> 160317; Since ColorPrimer is part of GangaCK, then xmlmerge & cleaner can
  benefit from this.

> 160317 xmlmerge: Safety - don't ask for delete if there's no merged output
> 160317 xmlmerge: Safety - don't ask for archive if there's still heavy files around

> 160311: gangacleaner: paralellize

> 160311: xmlmerge: Recommend archiving

> 160308: xmlmerge: Support merging for the metadata file
  - parsedxmlsummary, postprocesslocations
  - This allows better compat with archival of dir.
  - Resources on J4142

- 160308: Consider job's status "killed" as is_final too.
  - Motivation: caching partial-completed gen Gauss job.

> 160223: Got a script to check progress of Gauss@Dirac. This is experimental,
  use with care. It's also not yet integrated into main framework.

> 160218: cleaner: Check for dir (local/eos) of Gauss jobs. This is potentially deletable.

> 160218: merge ppl file together in case of xml archive?

> 160218: JobUtils, obtain list of EOS outputfiles from job


- 160212 Change gauss.nickname to staticmethod instead, as it's hardly depends
  on the version/platform of Gauss used. So it's also cachable.

> 160207: Collaborative ganga jobtree?
  - Use case; I need to share data with Aurelio, both metadata and actual tuple.
    How can this best be done?
  > Idea: no more gitfat --> eos. more standard.
    > Idea: Starts by list out all files currently manages by gitfat, and upload
      them to EOS, delete local file once uploaded.

> 160207 helper script to targz the subjobs in workspace dir.
  - Req: I want to preserve the structure inside archive
  - Req: It'll check existence of large file inside subjobs dir (root/dst),  
         warn user, and not continue further.
  - Req: It should be able to correctly delete subjobs dir
  - Req: It should do nothing in job with no subjobs.


https://stackoverflow.com/questions/6493270/why-is-tar-gz-still-much-more-common-than-tar-xz
tar -zcvf 4069.tar.gz . --exclude=output --> 5001055 bytes
tar -Jcvf 4006.tar.xz --exclude='./output' . -->  279828 bytes

tar -Jcvf data.tar.xz --exclude='./output' .
find . -maxdepth 1 -type d -name '[0-9]*' | xargs rm -rf; rm -rf debug/ input/


- 160119 ganga more nodes on jobtree json
  - Prelim: Try this: Adding foreign entry into the xml-json of jobtree. 
    Observe the change in behavior:
    - str: No good. jobtree.ls has an if-else loop such that this string keyval
      is considered as a job. val is tried to be casted as int for jid, thus
      integer exception is raised.
  - Thus, there's no way to add more information in that json data while make it
    compatible with vanilla's Ganga.
  - I may need to approach this by using shelve, read&write parallelly.

> 150707: jobShell optionally run into queues

> 150707: Print appchar legend

- Idea 160104: Given the now-frequent Sim08h recipe, is it possible to do whitelist
  on-demand flagged-mode S20 on-the-fly?
  - Idea: Patch on `StrippingStream.appendLines` method to accept only whitelisted
    lines into stream.
  - It'll be tricky to coordinate the namespace on both Ganga and DV.
  - How to pass variable into py file inside `importOptions`
    - in src code, it's just a wrapper around execfile.
    > global var (even if it's bad?)
    > sys.argv?


> Alternative parallel tech, see from Ganga code: C++ pointer to container style.
> How did they retrieve accessURL so fast!?
  - Ganga.GangaDirac.Lib.Splitters     : INFO     Requesting LFN replica info


> calling jv should have functionality of peek summary too ( sjid, backend, stderr table)
  Only to quick-view the error message. Diving into detail of single job should
  still be delegated to peek.

> cleaner: Remove subjobs if it deemed safe.

>  xmlmerge: Take replica into consideration when check for missing


> GangaCK: Patch Davinci.events, like Bender.events
  > Not easy to provide new attr. This is new.



### MyGanga ---> GangaCK



- LHCbDataset.new
  - Longer LHCbDataset cache expiredate
  - Move as classmethod instead of staticmethod
    - Thus, I do not need hardcoded LHCbDataset cls imported from GPI
  - LHCbDataset.new: Support copy constructor.
  > LHCbDataset.new: Support for pythonic input file (those with IOHelper inside)
    - Use case: Stripping dev already provide python file for testbed.
    - There's already buildin solution: `DaVinci().readInputData(...)`
      So I just need a wrapper around this.


- `OfflineGPI`, for the sake of testing.
  - This module mimic the functionality of other GPI, mainly the `config` 
    singleton at this stage. This is intended to replace the entire dependency
    on `from Ganga import GPI` in case of absence.
  - The `config` should do lookup with dynamic attribute access, e.g,
    `config.xxx.yyy` should just look for key yyy in section xxx automatically.
  - `gangrc_path` should check for existence of gangarc file.

- Misc enhancement
  - Let have the __patcher__.py for clarity
  - Ganga jrm guard: Any job inside JT cannot be deleted via jrm  
  - `ijob_handler` can now subclassing `cache_to_file`
    - This motivates the ABC for class-based decorator.


- OffineJob: subclass collections.Mapping for readonly-dict 


> Need LSF,Bender in OfflineGPI

> GangaCK: Move OfflineJob to OfflneGPI, interface with Enhanced Job

- Cache viewer
  - Foundation laid on base Decorator's shelf. Conform with iteration protocol.
  > It's just depends on which information I want to display in particular case
    like Ganga. I'll come back to this later after I have OfflineGPI.backend

> 


>>>>>>> Redesign OnlineJobtree to fallback to offline's by default.
>> Design question: When to draw a line between offline/online?
>> Is there really an advantage for the online info?

> QuickOnlineJobtreeReader (separate alternative interface from default-slow one)

> JT: Directory size
> Ganga async jt size
> Ganga: use .backend.getOutputDataLFNs
> JT: Time taken is more accurate if it exclude the finalization overhead.
  Determine this from the subjobs directly (find the last-finished one).
> force_reload cmdline arg for offline_ganga_reader?

> on-demand password ask for cluster backend

> Please, JT's disk usage to use full async. I don't want to wait!

> LHCbDataset.new from script with IOHelper inside (see StrippingTest)


> Use internal style __format__ for ganga jobtree
  - No need, the builtin __format__ works well with dictionary already. 
    So I can do something like '{name}.format(**J)' immediately.
  > Try implement this in current Jobtree, to allow custom representation 
    of a tree (for example, showing LPHE-cluster splitting scheme )
    > Do this after migrate OfflineJob to OfflineGPI


- Redesign 150814 note
  - Refactored `ConfigUtils` out from `Utils` which is more coupled to instance 
    of Config. It should be loaded very early (after OfflineGPI.Config, but 
    before the rest of OfflineGPI). In order to achieve this, ConfigUtils will 
    need to do late-import of GPI inside its method in order to avoid circular dep.

- GangaCK: Actually, there is no need to make the OfflineGPI reader protocol 
  convertible to dict. The primary demand is for offline-reading to __format__,
  and since it's support the attribute-protocol, just like what supposed to be 
  accessible Online, I can drop this support (BaseJsonablePropertyObject)

> Spacing-out: Looking for good TUI
  - Motivation: Imagine manipulating Ganga's Jobtree interactively with cursor,
    up/down to select dircetory, left/right to close, checking out for contents.
  - Early candidates: curtsies, npyscreen, urwid 
  > Let's start with: http://urwid.org/tutorial/index.html
  > Idea: OfflineGangaReader --> TUI --> open in root



> GangaCK: I should dump XML catalogue in local workspace/JID directory 
  (instead of /tmp used currently) So that it's better encapsulated & robust.

- GangaCK: Is there an elegant way to let it use fallback flag 
  `-o /Resources/StorageElements/DefaultProtocols=root` automatically in case 
  of resolved-accessURL yield file:/// protocol?
  - PlanA: Apply the flag above immediately at correct location.
    - The current core code relies on LHCbDataset.getCatalog method, which upon
      inspection delegated to another private method. Direct manipulation is 
      thus not possible.
  - PlanB: Provide patch on resultant PFN using pure string manip?
    - It's such a monkey-patching. Not really robust
    - However, this patch is only required for dataset at cnaf. limited enough.
    - Confirm first what prefix is possible with file:/// 
      - So far, only one case: 'root://xrootd-lhcb.cr.cnaf.infn.it/'
    - Remark: There're 2 places that need this patch
      1. At `uri_identifier` ( Use early by LHCbDataset.new )
      2. At `_rawxml_parser` ( Result from `LHCbDataset.getCatalog` )
  - Done! Effect can be seen in previously failed job on grid.
  - Remark: Cache need to be update to recieve this patch.


> reader: let offline_reader accept format template flag

- reader: More improvement on getitem syntax ( apart from getattr )
  - Motivated by the need for number of event from summary.xml, which is usually
    available at `j.metadata['events']['input']`



- better localizing Bender job on slurm
  - Move all dependency to `j.inputsandbox` (for 6.0) or `j.inputfiles` (for 6.1)
  - The order for `sys.path` needs to make sure that local comes first.
    - i.e., use `sys.path.insert(0, ...)`, not `sys.path.append(...)`
  - Rebuild the package everytime with `IOUtils.build_zippackage`. It's cheap.





- 150505 Streamlining ds.getCatalog(), let's cache it.
  - First, let's see what's the return of ds.getCatalog
    - It return a string, representing contents inside xml catalogue
  - Next, let's see what to put in the `XMLCatalogueSlice` attr
    - It takes `File` instance, but luckily it's overloaded for single string, 
      representing the path to xml file.
  - Finally, confirm that by putting catalogue slice, ganga uses this and reduce
    the submission time significantly for large ds. However, 
    - Confirm! (without splitter) it submits almost instantly
  - Now let's the hacking begin! Outlining...
    - Inside LHCbDataset.new, after filtered out the LFN uri, make a call to
      getCatalog instead of my DiracDMS.accessURL
    - Cache the result from getCatalog, index by lfn name, make this into repo
      - Cache1: Kitchensink. If list of lfns is passed, cache the entire xml
                string. Because this is not a good long-term index, only cache
                this for short period of time (dev purpose).
      - Cache2: Proper one indexed by lfn.
    - Need a plan B: Calling getCatalog on 6k files is going nowhere...
      - Perhaps the retrieval needs to be split into batch
    - Future call to LFN will then consult this repo first.
    > The repo can generate temp catalog file on-demand against request lfn,
      it return path to catalog, and put into resultant ds instance.
  > Design aim: Given a BKQ uri, return a path to xml
    - Because in reality, I expect ~6k LFN uri per single realdata BKQ uri.
      It's not gonna be better if the xml link is solely indexed on LFN.
      This would, nevertheless, be a higher level caching. (Think of it as 
      composite-index key).
Note: getCatalog is better than DiracDMS.accessURL because
1. catalog is natively support & prefered in Bender's `configure`
2. I don't need to write wrapper around sld myself. (required combination
   of lfn-metadata and lfn-accessURL to get the same data).

  

--------------------------------------------------------------------------------
                                CASES STUDY
--------------------------------------------------------------------------------

### 1508: Depreciate `run` command, in favor of magic
- src: '$GANGASYSROOT/ganga/python/Ganga/Runtime/IPythonMagic.py'
- Not cool. MyGanga library is loaded BEFORE the above binding. 
  Confirm that it'll be overrided by above command. So the decorative
  approach to override will not work.
- New trick! With this, it may be possible to change the import order
  - https://github.com/rmatev/ganga-tools/blob/master/GangaLHCbExt/__init__.py
- Nope, even moving as Plugin package, it's still not late enough.
- Finally, to avoid collision with `run` (from IPython) and `ganga`, 
  the new command is `grun`.


### 150929: Experimenting with new Ganga 6.1.8
There're also several issues regarding new Ganga v6.1.8 (v601r8). Goods & Bads
- PRO: Submission of jobs to grid starts to be more practical now. The new 
       splitter can splitting jobs more coherently across server. 
       While crunching the real data for Z02TauTau analysis, I don't see anymore
       bad dataset complains.
- PRO: Noticably faster startup/shutdown time.
- PRO: inputsandbox depreciated, use inputfiles instead. That's sweet.
- CON: New LHCbDataset constructor is insanely slow! Cause by the depreciation
       of LogicalFile. Internally it instantiate (large) list of DiracFile 
       instead, and that took some time. 1k files take ~1min.
- CON: Facing hang at some shutdown-time. But this may due to my experimentation.
- CON: New Splitter also does not play well with non-Dirac backend, especially 
       with LPHE's SLURM. The problem is, it somewhat discard the XMLcatalogue
       attached to LHCbDataset at split. With subjob's dataset have to XMLcat,
       it takes LOAD of time to retrieve the accessURL all over again.

  Because of the need to crunch through real data, given advantage of grid, 
but in exchange for unusable-SLURM, it was a tough exchange. In a long term  
it'll be nicer to work on the nwer version. Therefore, the current workaround 
is that old+new ganga will still both be used simultaneously. Use old one when 
submitting jobs to SLURM, and new one for submission to Dirac. For monitoring,
I can just use whichever I want. 

Note: As of 150930. I better stop doing Ganga experimentation while crunching 
through the real data. It's just not safe...

- Let's see, if I force job from failed to completed...
  - Will it recalculate total evt ?: 
    - No, if summary.xml is missing in one of them
  - Will old failed subjob remained failed (I want to, to keep track).
    - Yes, it remains fail, that's good.
  - Note: Tried under Ganga 6.1.8.


--------------------------------------------------------------------------------
                                   FEATURES
--------------------------------------------------------------------------------

### GangaTask
> Calling shell, with argparse


### JobTree
- Change Index to 1-index (for better handling of Index logic)
- Simplify indexing in BaseJobTreeReader ( no more self._cwd )
- offline: Support on my Mac OSX offline
- Fix offline ganga discrepancy --> bad gitignore
- Fix offline count for subjobs on osx
- Refactor magic-jt-whitelist-cmd, to JT's class (perhaps soon JobTreeWriter)
- Refactor JobtreeReader into subpackage
- Show summary of usage by drive (gangadir, massstorage, remote)
  - Remote storage next.
- JobtreeReader.print_tree --> repr
  - Need to decouple the logic around cwd
  - Properly fix the self.job(id) data format. Then refactor the delegating methods.
- Shorthad app name ([G]auss, [D]aVinci, [B]ender) 
- Longer comment columns.
- jt help --> Move docstring to `magic_jt`, accessible via jt?
- Fix `jt rm` directory display check.
- patch 1512: Be instanteneous!
  - Oh, using cElementTree instead (in DictTree class) got huge speedup!
  - Also changed the ET iterator to a generator version.
  - ConfigUtils.jids_repository: use os.walk, same speed, but less verbose.
  - OfflineJobtreereader with lazy jobs_all?
    - Fuck! It does get faster! The lazyness is justify since the offline instance
      is killed immediately, but the online version should NOT use this.
  - More @memorized in ConffigUtils, just be careful.
  - Done! This optimization gives me <1 sec returns!
- `find` command, by JID. 
  - Implemented in jobtree, so I just delegate.

> Comment of the directory?
> Offline_jobtree_writer
  > First: Lock & ignore request if some active ganga-session is found.  


### LHCbDataset
- Flag `ignore_missing` in case when LFN->PFN link is missing.
  - Perhaps site is down
- uri_identifier: 3 types : PFN,LFN,BKQ
  - To make things clear, I need to depreciate all BKQ inputs if it doesn't
    starts with new standard 'evt+std:/' or older 'evt://'. If shortname is
    given, don't accept it, because it looks too similar to single LFN.
- LHCbDataset.new: Merging 2 lhcbdataset, both with xmlcat
  - Need for construction of new ds from failed job (use their inputdata)
- Don't create & attach XMLcatalog if empty.
> 160107: Check support for large sample input, not necessary nested.
> 160107: Support for local envvar. 
  - For example, "$EOS_MGM_URL/$EOS_HOME/ganga/3968/87/Gauss-42102013-100ev-20160106.sim"
> 160216: Accept envvar in string, to use with $EOS_MGM_URL
> 160218: Check for unknown kwarg
> 160218: Auto EOS_MGM_URL? 
  - /eos/lhcb/... --> root://eoslhcb.cern.ch
  - /eos/user/... --> root://eosuser.cern.ch

### Shell
- `jrm -f`, with flag to force delete job already inside jobtree (which is 
  normally guarded against deletion).


### xmlmerge
- Migrated from PythonCK to GangaCK. More appropriate.
- Seperate directory size & (pending-merge) ntuple size.
  With this, it's clearer whether space taken was due to ntuple or just overhead.
- Ask for `hadd` over panfs. Lots of time is saved!
- Check for success in individual summaryxml. Be vigilant!
- 150108: If there's __jobstatus__, double check their status code.
- 160213: Use logging instead (but standalone, not from PythonCK).
  I want now the print+file simultaneously.
- 160216: Ask for deletion of subfiles after hadd


### cleaner
- EOS support.
  - Based on '$EOS_HOME' envvar.


### Misc
- GangaCK: Simple script to list all LFN in gangadir. Use as standalone script
  - `ganga_lfn_list.py`
  - It can be quite slow though...

