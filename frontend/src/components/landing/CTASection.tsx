export function CTASection() {
  return (
    <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">
            Ready to Deploy Multi-Agent Intelligence?
          </h2>
          
          <p className="text-xl mb-10 text-blue-100">
            Start building sophisticated AI systems that learn, adapt, and work together.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="px-8 py-4 bg-white text-blue-600 font-bold rounded-lg hover:bg-blue-50 transition">
              Get Started Free
            </button>
            <button className="px-8 py-4 border-2 border-white text-white font-bold rounded-lg hover:bg-white hover:text-blue-600 transition">
              View Documentation
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
