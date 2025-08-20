<?php

namespace App\Helpers;

class FileHelper
{
    public static function shareUrl($filePath)
    {
        $baseUrl = env('NAS_BASE_URL');
        return $baseUrl . '/' . ltrim($filePath, '/');
    }
}