"""Pin original plane initialization and initial sparse row refill; static only."""
import hashlib,json
from pathlib import Path
from inventory_rom import ROM_HASH
from m68k_static import Decoder

def catalogue(project):
    rom=(project/'local/rolo.md').read_bytes()
    if hashlib.sha256(rom).hexdigest()!=ROM_HASH:raise ValueError('ROM mismatch')
    inv=json.loads((project/'docs/stage9/inventory.json').read_text(encoding='utf-8'))
    accepted={address for routine in inv['routines'] for address in routine['blocks']}
    specifications=[
        (0x26c8,0x2746,'Original fixed initialization fill request',
         '26C8 setsC432bit0010, writes8F01(auto increment1), loads lengthregisters93/94fromD2, selectsfill9780, buildscommandfromD1address/D3code, publishesC462/C464, writesD0wordtodatalatch, pollsstatusbit0002untilclear, then clearsC432bit0010. For3CBCcaller: D0zero,D1B2A0,D2=127,D3=40000000. Nativelevel1initialization applies completed byteclearB2A0..B31F; extent is inferred from the original request plus externally documented Mode5 word-write/fill semantics, not a direct original-hardware capture.',
         'Other26C8caller domains, interrupt/FIFO interactions, completion timing and independent original-hardware initialized storage snapshot remain incomplete.'),
        (0x3c4c,0x3cd6,'Shared terrain pattern initialization order',
         'Clear512 quad records of8bytes and2048 pattern-cache words toFFFF, then128 visited macro bytes tozero. Load next pattern cursor from F264; scan foreground F30A then background F336 through3CD6 using the same caches/cursor. Publish resulting cursor back toF264. Request common artwork upload from053DC2 tobyteaddressB280, length06B0words via2466. Then requestzero DMA fill through26C8 with destinationB2A0 andlength007F, before returning. Native immutable services reproduce shared foreground/background scan and raw uploads; final zero fill is not yet bound.',
         'Initial F264 producer/value, native equivalent of final fill extent and completion timing, graphics queue ordering and original initialized storage comparison remain incomplete.'),
        (0x7292,0x72d0,'Foreground/background camera wrappers',
         '7292 selects foreground F30A and publishes active descriptor F302 before 72D0. 72A2 selects background F336 and publishes F302. C546 zero runs ordinary update. Nonzero C546 with nonnegative previous X tile at descriptor22 branches directly to 7424: only final offsets26=-X,28=Y change; shared camera globals remain untouched. Negative previous X saves descriptor18/20 as a long, clears both coordinates, calls full update, restores coordinates, then republishes final offsets. Native wrappers use explicit descriptor references; frozen initial refill preserves temporary zero-coordinate effects on prior tile words and shared globals.',
         'C546 writers/mode domains, active descriptor pointer users and complete frame scheduling/reference snapshots remain incomplete.'),
        (0x36ba,0x3784,'Plane descriptor initialization',
         'Foreground descriptorF30A ringbaseFFFF0000,rowcount64,shift6,rowmask1F80,columnmask03F0,size2000. BackgroundF336 baseFFFF4000,rowcount32,shift2,rowmask0F80,columnmask01F0,size1000. These descriptor sizes are not the full cleared memory extents. Loader3784 installs MAP pointers at+34; dimensions copied to+38/+40. F362long cleared,4018 called.',
         'Loader domains, descriptor alias writers and full frame initialization remain incomplete.'),
        (0x4020,0x4096,'Foreground/background backing clear',
         '4020 startsatFFFF4000 withDBF31;4030 startsatFFFF6000 withDBF15. Each iteration performs16 predecrementMOVEM writes of8longwords (512B). Foregroundclears16384B FFFF0000..3FFF; backgroundclears8192B FFFF4000..5FFF. Both preserve D0..D7/A0/A1. 4018 invokes both in order.',
         'Graphics/display users of the extra storage and shared RAM aliases require proof before compacting buffers.'),
        (0x4096,0x4158,'Initial sparse row refill',
         'D6=(descriptor20>>4)*2-18;D7=F374-0480. Horizontalwindow D4=max(unsignedBorrowClamp((descriptor18&FFF0)-0160),0),D5=D4+0400 wordwrap. Rowbudget=descriptor4-7 then predecrement each outerloop. Advance ringrowD7by80 maskeddescriptor8; advance rowindexD6by2 andskipnegative. MAP signedoffsetpair from+8/+10 defines rowrecords; equaloffsetskips. Nonempty row thenchecksunsigned D6againstMAPheight>>3. Halving/alignedbinarysearch narrows sortedX then sequential unsigned boundsD4<=X<D5.442A receives highwordtypeD0,recordpointerD1,X D3,rowcursorD7; saves/restores D4/D5. Empty-row/height-check order and postincrement pointer comparisons are literal.',
         '442A/446C continuation buffers, binary-search domains and malformed/out-of-range rows; incremental4158/417A/422C/4270/42BC/42E4 paths; camera/F374 producers and original-reference streaming snapshots remain incomplete.'),
        (0x4158,0x422c,'Entering row preparation and dispatch',
         '4158 setsA4=422C,rowindex=(descriptor20>>4)*2-16;negativewordreturnsbeforewrites;D7=F374-0400.417A setsA4=4270,rowindex=(descriptor20>>4)*2+2*descriptor6+001C,D7=((descriptor6+000E)<<7)+F374. Top clearcursor=D7;bottom clearcursor=D7+0380. Maskdescriptor8 thenadd80; clear128Bbeforecursor and128Bbeforecursor+descriptor14. Clearsprecedeunsignedheight>>3 check. Windowleft=max(unsignedborrowClamp((descriptor18&FFF0)-0160),0),right=left+0310 wrapping. MAPoffsetpair getsrowspan;emptyreturns;otherwiseJMPsavedA4. Nativeprepare_terrain_stream_row implements preparation through4210 only.',
         'MAP row spans and422C/4270 native refill; all descriptor/camera producer domains and independent buffer snapshots remain incomplete.'),
        (0x422c,0x42bc,'Ordered entering row refill searches',
         '422C searchesbackwardfromrowend usinghalvedwordlengthalignedto4 until<=8; scanspredecrementrecordpointer, skipsX>=right, stopsX<left; setsA4=4536 before446C withleftsaved.4270 searchesforwardfromrowstart, comparesunsignedXwithleft, thenboundsX<right; setsA4=44C4 before446C withrightsaved. Direction andcontinuationflags are partoforiginalordering, not interchangeable iteration over all map records.',
         'Search malformed/span/capacity domains and full446C native continuation semantics; column42BC/42E4 refill and updatephase producers remain incomplete.'),
        (0x42bc,0x442a,'Entering column clear and exact-X refill',
         'Bothentriesrowindex=(descriptor20>>4)*2-18,D7=F374-0480. Lefttarget=(descriptor18-0160)&FFF0;righttarget=(descriptor18&FFF0)+01A0 wordwrap. Clearcolumn=(lefttarget orrighttarget+00F0)>>3 &007E. DBF(descriptor4>>4)-1 clears32wordsperiteration at128Bstride, advancing4096B; foreground64 means128rows over16KB,background32means64rows over8KB. Clearhappensbefore rowrefillbudgetdescriptor4-7. Refillincrementsringcursor80maskeddescriptor8 androwindex2, skipsnegative rowindex, readsMAProwoffsetpairbeforeheightcheck, skips emptyrow. ForwardalignedbinarysearchfindstargetX; sequentialfallbackrequires exactunsignedXmatch.446C getsA4=45B4 withD4saved aroundcall; thenproceednextrow. Nativeprepare_terrain_stream_column implements preparation/clear through43B2 only.',
         'Nativeexact-X recordsearch and446C/45B4 copy, camera/update producers, malformed/zero count domains and independent reference snapshots remain incomplete.'),
        (0x44c4,0x463c,'Macro tile and metadata copy continuations',
         '44C4 replaces,4536 writesonlyemptytilewords,45B4 requiresunsignednewrecordoffsetD1>=oldmetadataword. Nonflagged descriptoradvancesA5byD0bytecountthenreadsbackward; startscolumnat scratch+widthBytesMinus2. Flaggeddescriptorreadsforward andtoggles tilebit12; columnsadvanceinstead. Both traverseringsrowsbottom-to-top, maskF2CA,maskcolumns007Eperword. Zero sourcewordpreservesbothbuffers. Metadatawordwrittenonlywithtile. Rowstride128; secondbufferseparationcomesfromsignextendeddescriptor14throughA1.462C restoresD6/D7upper/lowerhandoffs,popsscratchword,restoresA1fromUSP,A0fromF302. Nativecopy_terrain_macro implements wordcopybody withtypedhandoffinput; doesnotemulatecontinuationregisters.',
         '446Csetup/nativeMAPrecordbindings, signed separation caller domain, widths/heights/counttable consistency, special463Cspawns and independent original snapshots remain incomplete.'),
        (0x446c,0x44c4,'Normal descriptor typed handoff',
         'Unsignedtype>=0400redirects463Cbeforemacrolookup. Normaltype&007Fselectswordoffset+6inF2FAandbytecountwordB1EC. D3X LSR3suppliesscratchcolumn. Widthbyte2-2,heightbyte-1 andheightshift7plusD7preparecopy. D1recordpointerminusplaneMAPpointerbecomesparallelmetadata lowword. Plane14signextended suppliessecondbufferseparation. ANDFF00oforiginaltypeflagsselectforwardflagged/backwardunflaggedcopy. Native dispatch_terrain_descriptor bindsnormaltypedmacrodefinition/count/recordoffset tocopy_terrain_macro;463Cisrequiredseparateservice.',
         'Nativebankexport andrecordsearch/callerbindings, allsignedseparation/countdomains, initial442Arightclipgate andspecial463Cspawnsemantics remain incomplete.'),
        (0x442a,0x446c,'Initial macro width/right clipping',
         'Specialtype>=0400redirects463Cbeforelookup/clip. Normalmacroindex&7F selectsdefinitionandB1ECcount. ScratchX LSR3;widthbyte*2 comparedwith(rightwordLSR3)-scratch. Signednegativewrappedresultreturnswithoutcopy;zeroaccepts. Successfulsetupbranches449A sharednormalcopy. Nativedispatch_initial_terrain_descriptor preservesgate andrequiredspecialservice. Nativefill_initial_terrain joins4096rowbudget/search/copy; negativeinitialrowindicesadvancewithoutanotherbudgetdecrement, unlikecolumncaller.',
         'ActualF374/F2CA/cameraproducers, independentinitialbuffercomparison, special463Cspawn/worldordering andall malformedmacro/countdomains remain incomplete.'),
        (0x72d0,0x743c,'Camera tile crossing and terrain update order',
         'Publishplane12/14toF2CA/F2CC,cleardeltasF2CE/F2D0anddirectionbytesF36E..F371. Plane18/20LSR4storeprevious22/24. PreviousXnegativeorabsolute wrappedtile delta>2triggers75B0fullrefill. One/twotilecrossingssetdirectionflags andremaining(delta-1)<<4. Verticalupdatesfirst,thenhorizontal; two-stepupdatesusetemporarycoordinates beforefinalcoordinates.7588recomputedbeforeeachhelper. NegativeYcalls7450(top4158),positiveY743C(bottom417A);negativeX74F6(left42BC),positiveX74E2(right42E4). Finishplane26=-X,28=Y. Nativeupdate_terrain_camerapreservesliveglobals andexplicitclear/refill/row/columnservices.',
         'Bindnativebacking/displayservices,background7292/72A2wrappercontexts,planeidentityandallcameraaliaswriters; originalframe/displaycomparisons remain incomplete.'),
        (0x7588,0x75b0,'Ring coordinate publication',
         'F372=(plane18&03F0)>>3;F374=(plane20&plane10)<<3 wordwrap. Finalhardware8F02writeisnative displayservice responsibility. Native terrain_camera_ring_coordinates publishesactualsharedwordvalues.',
         'Native displayqueue equivalentandfullhardwareupdateordering notyetbound.'),
        (0x743c,0x74b6,'Native row name-table write setup',
         'Rowwrapperrefills417Aor4158first,then21metatilesrighttoleft. Bottomringrow=(F374+0700)&plane8,topF374;columnsF372+0028downby2masked007E. Columnwrapperrefills42E4or42BCfirst,then15metatilesbottomtotop;rightcolumn(F372+0028)&007E,leftF372. Tileindex&01FF selectsB2ECfourpatternwords; flags9000ORintobothwordpairs; bit12exchangestop/bottomdestinations whilepreservingwriteorder. Native terrain_display.hpp emits typed name-table rowwrites; TerrainStreamingCameraServicesjoinsrefillbeforedisplay.',
         'B2EC nativequadallocation/export,actualSDLnametable/rasterbinding,backgroundcontexts andindependentoriginalframecomparisons remain incomplete.'),
        (0x74b8,0x7588,'Native row tail and column name-table writes',
         'Rowtailhandles9000flags/verticaldestinationswap,then decrementscolumn2/DBF20. Columnwrapperrefillsfirst andemits15metatilesbottomtotop. Typednativewritespreservefourpatternwords andrelative name-table addresses. Bytes74B6..74B8 areexcludedfromthisaccepted-pathcontract: noacceptedentryat74B6,ordinarybranch74A6target74B8bypasses them.',
         'B2EC allocation/nativeexport,planeidentity/SDLbinding andindependentreferencecomparisons remain incomplete.'),
        (0x75d0,0x766a,'Native full plane display write order',
         'Fullredraw16rows bottomtotop starting0780,32metatilesrighttoleft starting62. Ringoffset=((F374+row)&plane8)+((F372+column)&007E). Relativepatternnameoffset=(ringoffset*2)&0F7C; secondpatternrowoffsetOR0080. Verticaltileflip swapsdestinations; priority/flipflagsORpatternwords. Native display_full_terrain emits1024typedrowwrites; caller75B0clear/initialrefill remainsbeforedisplay.',
         'Patternbankmapping,planebase/displaypriority andnativeSDLrenderbinding; originaldisplaytimingcomparison remain incomplete.'),
        (0x3cd6,0x3e04,'Initial MAP macro scan and quad remapping',
         'MAPfirstoffset8/finaloffset8+2*(height>>4)defineflatspan. Readrecordthenadvance4;unsignedcursor>=endreturnsbeforeprocessingthatrecord. Type>=0400skips;normaltypelowbyteindexesvisitedA98C,firstseenmarkedbeforemacrolookup. For eachmacro wordincludingzero usequadindex01FF. Commonquad<28 getsliteralADDI.L05940594ontwopackedlongs,includingcarryacrosswords. Bankquad>=28retainsF800flags andmaps7FFpatternthroughoriginal998Ctablewith2048wordslots. NegativecachedwordallocatesnextF264patternvia3E04. NativeTerrainQuadMappinghas2048patterns,512quadrecords,128visitedmacrobytes.',
         'Bindimmutablecommon/bankquadsource andgraphicsuploads,foreground/backgroundsharedscanordering,patterncursor/capacity andsignedmacrooffsetdomains; independentreferencepatternmapping remains incomplete.'),
        (0x3e04,0x3e2c,'First-seen pattern publication and upload',
         'StoreD6wordintopatternmapbeforesourceupload. SourcebyteaddressFFFF0000+(sourceindex*2word<<4word),targetpatternaddressD6<<5word;2466requests16words. OnreturnD2=D6,nextD6wordincrement1. Nativeupload_terrain_patternusesimmutabledecodedpatternsourceidentityandtargetindex; nativecachepublishedbeforecall, no inventedrollback.',
         '2466nativegraphicsqueue/sourcebinding,allcursor/capacitydomains andoriginaluploadtiming remain incomplete.')]
    operations=[]
    for start,end,name,contract,pending in specifications:
        cursor=start;evidence=[]
        while cursor<end:
            if cursor not in accepted:raise ValueError('Unaccepted instruction boundary '+hex(cursor))
            instruction=Decoder(rom,cursor).decode()
            evidence.append(instruction);cursor+=instruction['size']
        if cursor!=end:raise ValueError('Range end mismatch')
        operations.append(dict(entry=f'{start:06X}',end_exclusive=f'{end:06X}',name=name,contract=contract,pending=pending,instruction_evidence=evidence))
    source='src/core/terrain_stream_rows.hpp'
    if not (project/source).is_file():raise ValueError('Missing native row preparation')
    copy_source='src/core/terrain_macro_copy.hpp'
    if not (project/copy_source).is_file():raise ValueError('Missing native macro copy')
    descriptor_source='src/core/terrain_descriptor.hpp'
    if not (project/descriptor_source).is_file():raise ValueError('Missing native descriptor binding')
    search_source='src/core/terrain_record_search.hpp'
    if not (project/search_source).is_file():raise ValueError('Missing native record search')
    binding_source='src/core/terrain_streaming.hpp'
    if not (project/binding_source).is_file():raise ValueError('Missing native refill binding')
    camera_source='src/core/terrain_camera_update.hpp'
    if not (project/camera_source).is_file():raise ValueError('Missing native camera terrain update')
    display_source='src/core/terrain_display.hpp';world_source='src/core/terrain_camera_world.hpp'
    if not (project/display_source).is_file() or not (project/world_source).is_file():raise ValueError('Missing native terrain display/world binding')
    quad_source='src/core/terrain_quad_mapping.hpp'
    if not (project/quad_source).is_file():raise ValueError('Missing native quad mapping')
    return dict(rom_sha256=ROM_HASH,scope='Partial static terrain producer evidence, not native streaming or gameplay fidelity proof.',operations=operations,native_sources={'004158..004210':source,'0042BC..0043B2':source,'0044C4..00462C':copy_source,'00446C/00442A':descriptor_source,'00422C/004270/0043E4':search_source,'004096/004158/00417A/0042BC/0042E4':binding_source,'0072D0/007588':camera_source,'00743C..007588/0075D0':display_source,'camera_refill_binding':world_source,'003CD6/003E04':quad_source,'level1_pattern_initialization':'src/core/level1_terrain_patterns.hpp'},
        search_contract='Native ordered search uses live MAP byte reads and exact aligned halving. Forward binary equality bypasses upper gate; backward upper gate applies only while seeking first match. Sequential paths preserve read-before-pointer-bound comparison, requiring actual readable adjacent data domains. Callback actor/pointer effects outside normal446Crestoration remain pending.',complete_mapping=False,world_integrated=False)

if __name__=='__main__':
    project=Path(__file__).resolve().parents[1]
    report=catalogue(project)
    (project/'docs/stage9/terrain-streaming-contract.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print({'ranges':len(report['operations'])})
