<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\File;
use Illuminate\Support\Facades\Storage;

class FileUpload extends Controller
{
    public function createForm() {
        return view('file-upload');
    }

    public function fileUpload(Request $req) {
        $req->validate([
            'file' => 'required|file|mimes:jpg,jpeg,png,csv,txt,pdf|max:2048',
        ]);

        $fileModel = new File();

        if ($req->file()) {
            $fileName = time().'_'.$req->file->getClientOriginalName();
            $filePath = $req->file('file')->storeAs('uploads', $fileName, 'public');
            $fileModel->name = time().'_'.$req->file->getClientOriginalName();
            $fileModel->file_path = '/storage/' . $filePath;
            $fileModel->save();
            
            return back()
                ->with('success', 'File has been uploaded successfully.')
                ->with('file', $fileName);
        }
    }
}
