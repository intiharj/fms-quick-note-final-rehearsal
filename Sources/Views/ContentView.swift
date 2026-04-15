import SwiftUI
import FoxMountainKit

struct ContentView: View {
    var body: some View {
        TabView {
            NavigationStack {
                VStack(spacing: 16) {
                    Image(systemName: "square.stack.3d.up")
                        .font(.system(size: 42))
                        .foregroundStyle(FMColors.accent)

                    Text("Quick Note Final Rehearsal")
                        .font(FMFonts.title2)
                        .multilineTextAlignment(.center)

                    Text("Replace this placeholder screen with the core experience for Quick Note Final Rehearsal.")
                        .font(FMFonts.body)
                        .foregroundStyle(FMColors.textSecondary)
                        .multilineTextAlignment(.center)
                        .padding(.horizontal)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(FMColors.background)
                .navigationTitle("Home")
            }
            .tabItem {
                Label("Home", systemImage: "house")
            }

            NavigationStack {
                FMSettingsView(appName: "Quick Note Final Rehearsal", showPurchaseSection: false) {
                    Section("Setup") {
                        Text("Configure metadata, branding, monetization, and analytics before release.")
                    }
                }
            }
            .tabItem {
                Label("Settings", systemImage: "gear")
            }
        }
    }
}

#Preview {
    ContentView()
}
