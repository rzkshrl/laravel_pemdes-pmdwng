<?php
namespace App\Helpers;

class FilePathHelper
{
    public static function fullPath(string $relative): string {
    $base = rtrim(env('NAS_BASE_PATH',''),'/');
    return $base.'/'.ltrim($relative,'/');
    }
    public static function publicUrlFromRelative(string $relative): string {
    $baseUrl = rtrim(env('NAS_BASE_URL',''),'/');
    return $baseUrl ? $baseUrl.'/'.ltrim($relative,'/') : '';
    }
}