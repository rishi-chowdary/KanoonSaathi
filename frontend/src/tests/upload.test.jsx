import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import UploadPage from "../pages/UploadPage";

describe("UploadPage Component", () => {
  it("renders upload zone and policy notice", () => {
    render(
      <BrowserRouter>
        <UploadPage />
      </BrowserRouter>
    );

    expect(screen.getByText(/Upload Legal Document/i)).toBeInTheDocument();
    expect(screen.getByText(/Drag and drop your file here/i)).toBeInTheDocument();
    expect(screen.getByText(/Privacy & Data Grounding Policy/i)).toBeInTheDocument();
  });

  it("shows error when selecting an unsupported file format", () => {
    render(
      <BrowserRouter>
        <UploadPage />
      </BrowserRouter>
    );

    const input = document.querySelector('input[type="file"]');
    const invalidFile = new File(["dummy content"], "malicious.exe", { type: "application/x-msdownload" });

    fireEvent.change(input, { target: { files: [invalidFile] } });

    expect(screen.getByText(/Unsupported file format/i)).toBeInTheDocument();
  });

  it("shows error when selecting an empty file", () => {
    render(
      <BrowserRouter>
        <UploadPage />
      </BrowserRouter>
    );

    const input = document.querySelector('input[type="file"]');
    const emptyFile = new File([], "empty.pdf", { type: "application/pdf" });

    fireEvent.change(input, { target: { files: [emptyFile] } });

    expect(screen.getByText(/The selected file is empty/i)).toBeInTheDocument();
  });

  it("shows error when file exceeds 10MB limit", () => {
    render(
      <BrowserRouter>
        <UploadPage />
      </BrowserRouter>
    );

    const input = document.querySelector('input[type="file"]');
    const largeContent = new Uint8Array(11 * 1024 * 1024);
    const largeFile = new File([largeContent], "large_contract.pdf", { type: "application/pdf" });

    fireEvent.change(input, { target: { files: [largeFile] } });

    expect(screen.getByText(/File exceeds the 10MB limit/i)).toBeInTheDocument();
  });
});
