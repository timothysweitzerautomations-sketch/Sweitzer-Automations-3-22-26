import SwiftUI

struct ContentView: View {
    private let startURL = URL(string: "app://localhost/revenue_pulse/index.html")!

    var body: some View {
        WebView(url: startURL)
            .ignoresSafeArea()
#if os(macOS)
            .frame(minWidth: 900, minHeight: 600)
#endif
    }
}

#Preview {
    ContentView()
}
