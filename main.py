if ENVIRONMENT == "production":
                self.logger.info("🚀 Running in production mode")
                app.run(host="0.0.0.0", port=PORT, debug=True)
            else:
                self.logger.info("🔧 Running in development mode")
                app.run(host="0.0.0.0", port=PORT, debug=False)
                
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            raise
        finally:
            self.running = False
            self.db.close()
            self.logger.info("🛑 Bot shutdown complete")

def main():
    """Main entry point"""
    try:
        bot = MaprGuildMovieBot()
        bot.run()
    except Exception as e:
        logger = setup_logger(name)
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)

if name == "main":
    main()
