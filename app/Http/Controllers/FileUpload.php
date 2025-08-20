<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\File;
use App\Helpers\FilePathHelper;
use App\Services\SynologyFileStation;
use Illuminate\Support\Facades\Log; 
use Illuminate\Support\Facades\Storage;

class FileUpload extends Controller
{
  public function createForm()
  {
    return view('file-upload-nas');
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
        $files = File::all();
        return view('file-upload', compact('files'));
    }

    public function store(Request $request)
    {
        $request->validate([
            'file' => 'required|mimes:jpg,jpeg,png,pdf,doc,docx|max:5120', // 5MB
        ]);

        try {
            $uploadedFile = $request->file('file');

            // Simpan ke NAS (disk 'nas')
            $filePath = Storage::disk('nas')->putFile('', $uploadedFile);

            // Simpan ke DB (relative path saja)
            $file = File::create([
                'name'      => $uploadedFile->getClientOriginalName(),
                'file_path' => $filePath,
            ]);

            return back()->with('success', 'File berhasil diupload!')
                         ->with('file', $file);
        } catch (\Exception $e) {
            return back()->withErrors(['msg' => 'Upload gagal: ' . $e->getMessage()]);
        }
    }

    public function download($id)
    {
        $file = File::findOrFail($id);

        if (Storage::disk('nas')->exists($file->file_path)) {
            $fullPath = Storage::disk('nas')->path($file->file_path);
            return response()->download($fullPath, $file->name);
        }

        return back()->withErrors(['msg' => 'File tidak ditemukan.']);
    }
}