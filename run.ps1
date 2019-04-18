Import-Module powershell-yaml

[string[]]$fileContent = Get-Content "config.yml"
$content = ''
foreach ($line in $fileContent) { $content = $content + "`n" + $line }
$yaml = ConvertFrom-YAML $content

if($yaml.blender_path)
{
	if ($yaml.blend_file)
	{
		$command = $yaml.blender_path
		$args =  " -b " + '"' + $yaml.blend_file + '"' + " -P sprite_script_blender.py"
		invoke-expression "& `"$command`" $args"
	}
	else
	{
		"Please specify the blend_file path in config.yml"
	}
}
else
{
	"Please specify the path to the blender executable in config.yml"
}
