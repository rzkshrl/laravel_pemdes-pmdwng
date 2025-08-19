<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\File;
use App\Helpers\FilePathHelper;
use App\Services\SynologyFileStation;
use Illuminate\Support\Facades\Storage;

class FileUpload extends Controller
{
  public function createForm()
  {
    return view('file-upload');
  }

  public function fileUpload(Request $req)
  {
    $req->validate([
      'file' => 'required|file|mimes:jpg,jpeg,png,csv,txt,pdf|max:2048',
    ]);

    $fileModel = new File();

    if ($req->file()) {
      $fileName = time() . '_' . $req->file->getClientOriginalName();
      $filePath = $req->file('file')->storeAs('uploads', $fileName, 'public');
      $fileModel->name = time() . '_' . $req->file->getClientOriginalName();
      $fileModel->file_path = '/storage/' . $filePath;
      $fileModel->save();

      return back()
        ->with('success', 'File has been uploaded successfully.')
        ->with('file', $fileName);
    }
  }

  public function index()
  {
    $files = File::latest()->get();
    return view('file-upload-nas', compact('files'));
  }

  public function store(Request $request, SynologyFileStation $fs)
  {
    $request->validate([
      'file' => 'required|mimes:jpg,png,pdf,doc,docx,xls,xlsx,txt|max:20480',
    ]);
    $f = $request->file('file');
    $folder = trim(env('NAS_RELATIVE_FOLDER', 'uploads'), '/');
    $name = time() . '_' . $f->getClientOriginalName();

    // simpan ke NAS via disk 'nas'
    Storage::disk('nas')->putFileAs($folder, $f, $name);

    $relative = $folder . '/' . $name;
    $absolute = FilePathHelper::fullPath($relative);

    // buat public link
    // $shareUrl = $fs->createShareLink($absolute);

    File::create([
      'name' => $name,
      'file_path' => $relative, // relative path saja
      'share_url' => null,
    ]);

    return back()->with('success', 'File berhasil diupload dan link publik dibuat.');
  }
}