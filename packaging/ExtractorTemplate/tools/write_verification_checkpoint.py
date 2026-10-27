import json,re
from pathlib import Path
p=Path(__file__).resolve().parents[1];docs=p/'docs/stage9';root=p.parents[1]
inv=json.loads((docs/'inventory.json').read_text());green=[r for r in inv['routines'] if r.get('verification_status')=='verified'];unknown=[r for r in inv['routines'] if r['status']=='unassessed'];total=len(inv['routines']);assessed=total-len(unknown);partial=assessed-len(green)
from inventory_level1_batch import catalogue
batch=catalogue(p);addresses=set(batch['candidate_addresses']);pending=[r for r in unknown if r['address'] in addresses and r['subsystem']=='unassigned'];(docs/'level1-current-candidates.json').write_text(json.dumps(batch,indent=2)+'\n')
(docs/'level1-unassigned-next-batch.json').write_text(json.dumps(dict(scope='Conservative Level1candidate graph, includes shared/bootstrappaths; not allproven actuallevelbehaviour',entries=[dict(address=r['address'],hex=r['hex'],instruction_count=r['instruction_count']) for r in pending]),indent=2)+'\n')
checklist=docs/'LEVEL1-COMPLETE-CHECKLIST.md';s=checklist.read_text(encoding='utf-8').split('## Routine candidates')[0];s+='## Routine candidates\n\n'+str(len(addresses))+' conservative candidate addresses; '+str(len(pending))+' remain unassigned/unassessed. Green is the declared local API contract, not fulllevelcertification.\n\n| ROM address | Assessment |\n|---|---|\n';rs={r['address']:r for r in inv['routines']}
for a in sorted(addresses):s+=f'| `${a:06X}` | {rs.get(a,{}).get("status","Candidate outside routine entry list")} |\n'
checklist.write_text(s,encoding='utf-8')
ledger=['# Verified native contracts','',f'{len(green)} local contracts green; {partial} partial; {len(unknown)} unassessed; total{total}. Assessment{assessed}/{total}={assessed/total:.1%}; verified{len(green)}/{total}={len(green)/total:.1%}. No fulllevelcertificate.','', '| Address | Verified scope and evidence |','|---|---|']
for r in green:ledger.append(f'| `${r["hex"]}` | {r["status"]}; {r.get("verification_evidence","")} |')
ledger+=['','Declared valid-input domains and service/API boundaries are in each evidence report. CPUtemporaryregisters/CCR/ABI are replaced by nativeAPI. Green does not certify allcallers, data publication, device timing or entire gameplay. Some standalone helpers stillawaitlivecallerbindings.','', 'Original forest artwork export is verified separately; it is not counted as a routine. Reproduce local tests/reports through verify-level1-contracts.ps1.','']
(docs/'VERIFIED-COMPONENTS.md').write_text('\n'.join(ledger),encoding='utf-8')
percent=docs/'PROGRESS-PERCENTAGES.md';s=percent.read_text(encoding='utf-8');s=re.sub(r'\*\*Overall ROM assessment:.*?\*\*',f'**Overall ROM assessment: {assessed}/{total} = {assessed/total:.1%}. Verified local native routine contracts: {len(green)}/{total} = {len(green)/total:.1%}.**',s);percent.write_text(s,encoding='utf-8')
summary=f'''# Latest authoritative checkpoint — 14 October 2026

{len(green)}green/{partial}partial/{len(unknown)}unassessed of{total}; {assessed/total:.1%}assessed; {len(green)/total:.1%}verifiedlocalcontracts. {len(pending)}unassigned/unassessedLevel1conservativecandidates. 1438calls,50uniquecontrol-flow sites. Green domains are local API/state proofs, not full CPU ABI, caller, hardware or level certificates. Playable estimates unchanged80%Level1/75%Level2.

New green9504/9514/9524finitechainflags,34C2graphics-span state/diagnosticrequest,8F22full linkedobject-overlapquery,9012playercontactgeometry/latches,C920companiontarget,86D6ceilingquery. Original artworkbaseline preserved. Nativechainclear connected toStartmenu, companionselectionanddamageblink; toggle connected todamageblink. Sharedobjectcontactnowusescertifiedfullchainquery. Newnativehelpers/testsources include actor_chain_flag.hpp and object-overlapquery. Focusednative tests pass, includingLevel1/2Startmenu/damageblink andexistingobjectcontacttest. Dynamic support8A68/8BAC andpatchpublication8D4E plus10wrappers assessedpartial; nativebindings/statealiases remainopen. NoROMinstructionexecution.

Reproduce via verify-level1-contracts.ps1: focused native contract executables plus menu/bounce callback integration, orderedproofreports andinventory/worklist. Greenreports sourcehashpinned andfailifstale; changesneedtargetedrebuild/reproof. Update graph with work/draw_mapping_progress.py and ledger/checkpoint with tools/write_verification_checkpoint.py. Continue remainingunassignedLevel1entries andcaller/selectorclosure, avoidingfalsegreenfragmententries (2A18 is inlinewithinactivescan, not leafRTS). Ordinaryallowanceonly, neverbuy/useresetcredits. Goaltool stillusageLimited andcannotresumeit; userauthorisedcurrentwork. Savecheckpointregularly.

'''
resume=docs/'RESUME.md';resume.write_text(summary+resume.read_text(encoding='utf-8'),encoding='utf-8');print(json.dumps(dict(green=len(green),partial=partial,unassessed=len(unknown),level1_unassigned=len(pending))))
