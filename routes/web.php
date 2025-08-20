<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\FileUpload;

Route::get('/', function () {
    return view('welcome');
});

// Route::get('/upload-file', [FileUpload::class, 'createForm']);
// Route::post('/upload-file', [FileUpload::class, 'fileUpload'])->name('fileUpload');

Route::get('/upload', [FileUpload::class, 'index'])->name('file.index');
Route::post('/upload', [FileUpload::class, 'store'])->name('file.upload');
Route::get('/file-download/{id}', [FileUpload::class, 'download'])->name('file.download');