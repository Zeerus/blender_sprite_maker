Install-Module powershell-yaml

Import-Module powershell-yaml
[string[]]$fileContent = Get-Content "config.yml"
$content = ''
foreach ($line in $fileContent) { $content = $content + "`n" + $line }
$yaml = ConvertFrom-YAML $content

if($yaml.blender_python_path)
{
	$command = $yaml.blender_python_path
	$args =  " -m ensurepip"
	invoke-expression "& `"$command`" $args"

	$args =  " -m pip install pyyaml Pillow"
	invoke-expression "& `"$command`" $args"	
}
else
{
	"Please specify the blender python path in config.yml"
}
