#!powershell
# WANT_JSON
# POWERSHELL_COMMON
# ansible win -i inventory -M ./library -m win_vagr -a "path=D:\VAGRANT vmname=vm state=started"

$params = Parse-Args $args -supports_check_mode $true
$VagrantPath = Get-AnsibleParam -obj $params -name "path" -type "str"
$VMName = Get-AnsibleParam -obj $params -name "vmname" -type "str"
$SetState = Get-AnsibleParam -obj $params -name "state" -type "str"

$VFailed = $false

if ($VMName -eq $null) { $VMName = 'default' } 

if ($VagrantPath -eq $null){
    $VFailed = $true
    $FMsg='Missing required argument path. '    
}elseif ( ( Test-Path $VagrantPath ) -eq $false ) {
    $VFailed = $true
    $FMsg='Path to vagrantfile is not correct. '    
}

if ($SetState -eq $null){
    $VFailed = $true
    $FMsg=$FMsg+'Missing required argument state .'    
}elseif (( $SetState -match 'started|stopped|destroyed') -eq $false) {    
    $VFailed = $true
    $FMsg=$FMsg+'Argument state must be - started, stopped or destroyed. '    
}

if($VFailed) {
    $result = @{
        failed = $VFailed
        msg=$FMsg    
    }
    Exit-Json $result
}

#$VagrantPath=$VagrantPath.ToUpper()    
Set-Location $VagrantPath

$VagrantOut = (& 'vagrant' 'status')
foreach ($OutStr in $VagrantOut) {
   if($OutStr -match $VMName) {
      if($OutStr -match 'running')         { $VState = 'running' }
      elseif($OutStr -match 'not created') { $VState = 'not created' }
      elseif($OutStr -match 'poweroff')    { $VState = 'poweroff' }
   }
}

$VChange = $false
 
if ($SetState -eq 'started'){
    if($VState -ne 'running') { & 'vagrant' 'up' "'$VMName'"; $VChange = $true;}
}elseif ($SetState -eq 'stopped') {
        if ($VState -eq 'not created') { & 'vagrant' 'up' "'$VMName'"}
        if ($VState -ne 'poweroff' )   { & 'vagrant' 'halt' "'$VMName'"; $VChange = $true;}
}elseif ($SetState -eq 'destroyed') {
        if ($VState -ne 'not created') { & 'vagrant' 'destroy' '--force' "'$VMName'"; $VChange = $true;} 
}

$VagrantOut = (& 'vagrant' 'status')
foreach ($OutStr in $VagrantOut) {
   if($OutStr -match $VMName) {
      if($OutStr -match 'running')     { $VState = 'running' }
      elseif($OutStr -match 'not created') { $VState = 'not created' }
      elseif($OutStr -match 'poweroff')    { $VState = 'poweroff' }
   }
}

if($VState -ne 'running') {
    $result = @{
        state = $VState
        changed = $VChange    
    }
    Exit-Json $result
}

$VagrantOut = (& 'vagrant' 'ssh-config' "'$VMName'")
foreach ($OutStr in $VagrantOut) {
   if($OutStr -match 'HostName')            { $VLIp = $OutStr.split(' ')[-1] }
   elseif($OutStr -match 'Port')            { $VPort = $OutStr.split(' ')[-1] }
   elseif($OutStr -match 'IdentityFile')    { $VKey = $OutStr.split(' ')[-1]}
   elseif($OutStr -match 'User ')           { $VUser = $OutStr.split(' ')[-1] }
}

$VIp = (& 'vagrant' 'ssh' "'$VMName'" '-c' "ip a list eth1 | sed -n '3 {s/^.*inet \([0-9.]*\).*/\1/;p}'")

$VagrantOut = (& 'vagrant' 'ssh' "'$VMName'" '-c' 'cat /proc/meminfo')

foreach ($OutStr in $VagrantOut) {
   if($OutStr -match 'MemTotal')    { $VRam = $OutStr.split(' ')[-2]}
}

$VOs = (& 'vagrant' 'ssh' "'$VMName'" '-c' 'cat /etc/redhat-release')

$VKey = $VKey -replace '^.:', ''
$VKey = $VKey.ToLower()

$result = @{
  changed = $VChange    
  state = $VState
  ipaddr = $VIp
  iploc = $VLIp
  port = $VPort
  keypath = $VKey
  userlogin = $VUser
  os_name = $VOs
  ramsize = $VRam
}

Exit-Json $result
