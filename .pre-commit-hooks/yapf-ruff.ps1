#!/usr/bin/env pwsh

Set-StrictMode -Version Latest
$ErrorActionPreference = "stop"

$defaultOptions = @{
	PassThru = $true
	Wait = $true
	NoNewWindow = $true
}

$yapfOptions = @{
	FilePath = "yapf.exe"
	ArgumentList =
	  "-i",
	#   "-vv",
	  "$args"
}

$yapfOutput = Start-Process @yapfOptions @defaultOptions

if ($yapfOutput.ExitCode -ne 0) {
	exit $yapfOutput.ExitCode
}

$ruffOptions = @{
	FilePath = "ruff.exe"
	ArgumentList =
	  "check",
	  "--force-exclude",
	  "--fix",
	  "--exit-non-zero-on-fix",
	  "--config=./pyproject.toml",
	  "$args"
}
$ruffOutput = Start-Process @ruffOptions @defaultOptions

if ($ruffOutput.ExitCode -ne 0) {
	exit $ruffOutput.ExitCode
}
