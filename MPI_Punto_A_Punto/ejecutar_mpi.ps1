# Script para compilar y ejecutar mpi_punto_a_punto.c en Windows usando MS-MPI y GCC

# Cambiar la ubicación actual al directorio del propio script
Set-Location $PSScriptRoot

# Configurar las variables de entorno locales para la sesión de PowerShell
$env:Path = "C:\Program Files\Microsoft MPI\Bin\;" + $env:Path
$env:MSMPI_INC = "C:\Program Files (x86)\Microsoft SDKs\MPI\Include"
$env:MSMPI_LIB64 = "C:\Program Files (x86)\Microsoft SDKs\MPI\Lib\x64"

Write-Host "Compilando mpi_punto_a_punto.c..." -ForegroundColor Cyan
gcc -o mpi_punto_a_punto.exe mpi_punto_a_punto.c -I"$env:MSMPI_INC" -L"$env:MSMPI_LIB64" -lmsmpi

if ($LASTEXITCODE -eq 0) {
    Write-Host "Compilacion exitosa. Ejecutando con mpiexec (2 procesos)...`n" -ForegroundColor Green
    mpiexec -n 2 .\mpi_punto_a_punto.exe
} else {
    Write-Host "Error en la compilacion." -ForegroundColor Red
}
