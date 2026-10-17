import json,os,re
from pathlib import Path
package=json.loads(Path('package.json').read_text());ref=os.environ['GITHUB_REF']
dev=ref=='refs/heads/develop'
if dev:
    version=package['version'].split('-')[0]+'-dev.'+os.environ['GITHUB_RUN_NUMBER'];package['version']=version
    Path('package.json').write_text(json.dumps(package,indent=2)+'\n')
    lock=json.loads(Path('package-lock.json').read_text());lock['version']=version;lock['packages']['']['version']=version;Path('package-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
else:
    version=package['version']
    if not re.fullmatch(r'\d+\.\d+\.\d+',version) or ref!='refs/tags/v'+version:raise SystemExit('Stable tag must match package.json X.Y.Z')
with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('tag=v'+version+'\nprerelease='+str(dev).lower()+'\n')
