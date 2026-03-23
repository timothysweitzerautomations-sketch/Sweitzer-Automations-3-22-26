import Foundation
import UniformTypeIdentifiers
import WebKit

/// Serves bundled `revenue_pulse/` under the `app` URL scheme so relative links and fetch() work like HTTP.
final class AppSchemeHandler: NSObject, WKURLSchemeHandler {
    func webView(_ webView: WKWebView, stop urlSchemeTask: WKURLSchemeTask) {}

    func webView(_ webView: WKWebView, start urlSchemeTask: WKURLSchemeTask) {
        guard let url = urlSchemeTask.request.url else {
            urlSchemeTask.didFailWithError(URLError(.badURL))
            return
        }

        let path = url.path.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        let parts = path.split(separator: "/").map(String.init)
        guard parts.first == "revenue_pulse", !parts.contains("..") else {
            urlSchemeTask.didFailWithError(URLError(.fileDoesNotExist))
            return
        }

        let relative = parts.dropFirst().joined(separator: "/")
        guard let base = Bundle.main.resourceURL else {
            urlSchemeTask.didFailWithError(URLError(.fileDoesNotExist))
            return
        }

        let fileURL = base.appendingPathComponent("revenue_pulse").appendingPathComponent(relative)
        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            urlSchemeTask.didFailWithError(URLError(.fileDoesNotExist))
            return
        }

        do {
            let data = try Data(contentsOf: fileURL)
            let mime = Self.mimeType(for: fileURL)
            let response = URLResponse(
                url: url,
                mimeType: mime,
                expectedContentLength: data.count,
                textEncodingName: mime.hasPrefix("text/") ? "utf-8" : nil,
            )
            urlSchemeTask.didReceive(response)
            urlSchemeTask.didReceive(data)
            urlSchemeTask.didFinish()
        } catch {
            urlSchemeTask.didFailWithError(error)
        }
    }

    private static func mimeType(for url: URL) -> String {
        if let type = UTType(filenameExtension: url.pathExtension),
           let preferred = type.preferredMIMEType {
            return preferred
        }
        switch url.pathExtension.lowercased() {
        case "html", "htm": return "text/html"
        case "csv": return "text/csv"
        case "css": return "text/css"
        case "js": return "application/javascript"
        case "json": return "application/json"
        case "png": return "image/png"
        case "jpg", "jpeg": return "image/jpeg"
        case "svg": return "image/svg+xml"
        default: return "application/octet-stream"
        }
    }
}
