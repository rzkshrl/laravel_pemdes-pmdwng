<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use App\Helpers\FileHelper;

class File extends Model
{
    protected $fillable = ['name', 'file_path'];

    protected $appends = ['share_url'];

    public function getShareUrlAttribute()
    {
        return FileHelper::shareUrl($this->file_path);
    }
}