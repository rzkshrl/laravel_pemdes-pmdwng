<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\File;
use App\Helpers\FilePathHelper;
use App\Services\SynologyFileStation;
use Illuminate\Support\Facades\Log; 

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
        'file' => 'required|mimes:jpg,jpeg,png,pdf,docx,xlsx|max:20480'
    ]);

    // Lokasi NAS di luar project Laravel
    $outsidePath = '/volume1/DriveShare/uploads';
    if (!file_exists($outsidePath)) {
        mkdir($outsidePath, 0775, true);
    }

    $file = $request->file('file');
    $fileName = time() . '_' . $file->getClientOriginalName();

    // Simpan ke NAS
    $file->move($outsidePath, $fileName);

    // Path relatif yg disimpan ke DB
    $relativePath = 'DriveShare/uploads/' . $fileName;

    // Default share URL null
    $shareUrl = null;

    try {
        // Coba generate public link via helper
        $shareUrl = SynologyFileStation::createPublicLink($relativePath);
    } catch (\Exception $e) {
        // Kalau gagal jangan bikin error 500, cukup log
        Log::error("Gagal generate share link: " . $e->getMessage());
        $shareUrl = null;
    }

    // Simpan ke DB
    \App\Models\File::create([
        'name' => $fileName,
        'file_path' => $relativePath,
        'share_url' => $shareUrl,
    ]);

    return redirect()->back()->with('success', 'File berhasil diupload!');
  }
}