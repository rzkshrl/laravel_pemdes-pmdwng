<?php
namespace App\Helpers;

class FilePathHelper
{
    public static function fullPath(string $relative): string {
    $base = rtrim(env('NAS_BASE_PATH','/volume1/homes/adminpemdes/PemdesData'),'/');
    return $base.'/'.ltrim($relative,'/');
    }
    public static function publicUrlFromRelative(string $relative): string {
    $baseUrl = rtrim(env('NAS_BASE_URL','/volume1/homes/adminpemdes/PemdesData'),'/');
    return $baseUrl ? $baseUrl.'/'.ltrim($relative,'/') : '';
    }
}